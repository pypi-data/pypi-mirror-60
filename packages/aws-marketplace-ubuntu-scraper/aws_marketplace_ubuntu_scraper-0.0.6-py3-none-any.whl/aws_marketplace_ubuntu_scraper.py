import json
import re
import sys
import time

import boto3
import click
import requests

from collections import OrderedDict

from bs4 import BeautifulSoup
from joblib import Parallel, delayed
from selenium.webdriver.firefox.options import Options
from seleniumwire import webdriver

CANONICAL_OWNER = "099720109477"
CANONICAL_MARKETPLACE_PROFILE = "565feec9-3d43-413e-9760-c651546613f2"


def get_regions(account_id, username, password, headless):
    driver_options = Options()
    driver_options.headless = headless
    driver = webdriver.Firefox(options=driver_options)
    wait = webdriver.support.ui.WebDriverWait(driver, 10)
    driver.get("https://{}.signin.aws.amazon.com/console".format(account_id))
    username_element = driver.find_element_by_id("username")
    username_element.send_keys(username)
    password_element = driver.find_element_by_id("password")
    password_element.send_keys(password)
    driver.find_element_by_id("signin_button").click()
    wait.until(lambda driver: driver.find_element_by_name("awsc-mezz-data"))
    region_list_element = driver.find_element_by_name("awsc-mezz-data")
    region_list_str = region_list_element.get_attribute("content")
    region_list = json.loads(region_list_str)["regions"]

    driver.delete_all_cookies()
    driver.close()
    driver.quit()
    return region_list


@click.command()
@click.option(
    "--iam-account-id",
    envvar="IAM_ACCOUNT_ID",
    required=True,
    help="IAM User account ID",
)
@click.option(
    "--iam-username", envvar="IAM_USERNAME", required=True, help="IAM username"
)
@click.option(
    "--iam-password", envvar="IAM_PASSWORD", required=True, help="IAM User account ID"
)
@click.option(
    "--headless/--no-headless",
    default=True,
    help="Use selenium in headless mode to avoid Firefox browser opening",
)
def quicklaunch(iam_account_id, iam_username, iam_password, headless):
    region_dict_list = get_regions(iam_account_id, iam_username, iam_password, headless)
    driver_options = Options()
    driver_options.headless = headless

    def scrape_quicklaunch_regions(region_dict):
        def get_ami_details(region_client, ami, quickstart_slot, ami_id):
            # Get the ami details
            resp = region_client.describe_images(
                Owners=[CANONICAL_OWNER],
                Filters=[{"Name": "image-id", "Values": [ami_id]}],
            )
            resp_len = len(resp.get("Images", []))
            if resp_len:  # This is a Canonical AMI
                name_regex = (
                    r"ubuntu/images(-(?P<imgtype_path>[\w-]+))?/"
                    r"((?P<virt_storage>\w+(-\w+)?)/)?"
                    r"ubuntu-(?P<suite>\w+)-"
                    r"((?P<release_version>\d\d\.\d\d)-)?"
                    r"((?P<upload_type>\w+)-)?"
                    r"(?P<arch>\w+)-server-"
                    r"(?P<serial>\d+(\.\d{1,2})?)"
                    r"(\-(?P<custom>\w+))?"
                )
                name = resp["Images"][0]["Name"]
                match = re.match(name_regex, name)
                if not match:
                    raise Exception("Image name {} could not be parsed".format(name))
                attrs = match.groupdict()
                ami["quickstart_slot"] = quickstart_slot
                ami["ami_id"] = ami_id
                for key, value in attrs.items():
                    ami[key] = value
                return ami
            else:
                return None
        region_identifier = region_dict["id"]
        print("scraping {} ...".format(region_identifier))
        region_session = boto3.Session(region_name=region_identifier)
        region_client = region_session.client("ec2")

        driver = webdriver.Firefox(options=driver_options)
        wait = webdriver.support.ui.WebDriverWait(driver, 20)
        driver.get("https://{}.signin.aws.amazon.com/console".format(iam_account_id))
        username_element = driver.find_element_by_id("username")
        username_element.send_keys(iam_username)
        password_element = driver.find_element_by_id("password")
        password_element.send_keys(iam_password)
        driver.find_element_by_id("signin_button").click()

        wait.until(lambda driver: driver.find_element_by_id("nav-regionMenu"))
        driver.find_element_by_id("nav-regionMenu").click()
        # Are we on the correct region already?
        region_full_name = "{} ({}){}".format(
            region_dict["name"], region_dict["location"], region_identifier
        )
        current_region_element = driver.find_element_by_class_name("current-region")
        if current_region_element.text != region_full_name:
            wait.until(
                lambda driver: driver.find_element_by_xpath(
                    '//a[@data-region-id="{}"]'.format(region_identifier)
                )
            )
            driver.find_element_by_xpath(
                '//a[@data-region-id="{}"]'.format(region_identifier)
            ).click()
        else:
            driver.find_element_by_id("nav-regionMenu").click()

        wait.until(lambda driver: driver.find_element_by_id("nav-servicesMenu"))
        driver.find_element_by_id("nav-servicesMenu").click()
        wait.until(
            lambda driver: driver.find_element_by_xpath('//li[@data-service-id="ec2"]')
        )
        driver.find_element_by_xpath('//li[@data-service-id="ec2"]/a').click()
        wait.until(
            lambda driver: driver.find_element_by_xpath('//iframe[contains(@id, "-react-frame")]')
        )
        dashboard_iframe = driver.find_element_by_xpath('//iframe[contains(@id, "-react-frame")]')
        driver.switch_to.frame(dashboard_iframe)
        wait.until(
            lambda driver: driver.find_element_by_class_name(
                "awsui-button-dropdown-container")
        )
        print("{} - Opening launch instance page".format(region_identifier))
        driver.find_element_by_class_name("awsui-button-dropdown-container").click()
        wait.until(
            lambda driver: driver.find_element_by_xpath("//*[contains(@href, '#LaunchInstanceWizard:')]")
        )
        driver.find_element_by_xpath("//*[contains(@href, '#LaunchInstanceWizard:')]").click()
        driver.switch_to.default_content()
        wait.until(
            lambda driver: driver.find_element_by_id("gwt-debug-tab-QUICKSTART_AMIS")
        )
        driver.find_element_by_id("gwt-debug-tab-QUICKSTART_AMIS").click()
        wait.until(
            lambda driver: driver.find_element_by_id("gwt-debug-tab-QUICKSTART_AMIS")
        )
        wait.until(lambda driver: driver.find_element_by_id("gwt-debug-paginatorLabel"))
        # wait until JSON request is complete loads.
        # 3 seconds seems to be enough for all regions
        print("{} - Querying quickstart list".format(region_identifier))
        time.sleep(3)
        for request in list(driver.requests):
            if "call=getQuickstartList" in request.path and request.response:
                region_quickstart_entries = json.loads(request.response.body)
                ubuntu_quick_start_listings = []
                quickstart_slot = 0
                for ami in region_quickstart_entries["amiList"]:
                    quickstart_slot = quickstart_slot + 1
                    if ami["platform"] == "ubuntu":
                        if ami.get("imageId64", None):
                            canonical_amd64_ami = get_ami_details(
                                region_client,
                                ami.copy(),
                                quickstart_slot,
                                ami.get("imageId64"),
                            )
                            if canonical_amd64_ami:
                                ubuntu_quick_start_listings.append(canonical_amd64_ami)

                        if ami.get("imageIdArm64", None):
                            canonical_arm64_ami = get_ami_details(
                                region_client,
                                ami.copy(),
                                quickstart_slot,
                                ami.get("imageIdArm64"),
                            )
                            if canonical_arm64_ami:
                                ubuntu_quick_start_listings.append(canonical_arm64_ami)

                # We only need one list so we can break here
                break

        driver.delete_all_cookies()
        driver.close()
        driver.quit()
        return (region_identifier, ubuntu_quick_start_listings)
    n_jobs = -1
    parallel_quickstart_entries = Parallel(n_jobs=n_jobs)(
        delayed(scrape_quicklaunch_regions)(region_dict)
        for region_dict in region_dict_list
    )

    sorted_parallel_quickstart_entries = sorted(
        parallel_quickstart_entries, key=lambda tup: tup[0]
    )
    for region, ubuntu_quickstart_entries in sorted_parallel_quickstart_entries:
        print(region)
        for ubuntu_quickstart_entry in ubuntu_quickstart_entries:
            print(
                "{} {} {} {} (Slot: {} , Title: {}, Description: {})".format(
                    ubuntu_quickstart_entry["release_version"],
                    ubuntu_quickstart_entry["serial"],
                    ubuntu_quickstart_entry["arch"],
                    ubuntu_quickstart_entry["ami_id"],
                    ubuntu_quickstart_entry["quickstart_slot"],
                    ubuntu_quickstart_entry["title"],
                    ubuntu_quickstart_entry["description"],
                )
            )
        print()


@click.command()
def marketplace():
    public_profile_url_base = "https://aws.amazon.com/marketplace/seller-profile"
    public_profile_url = "{}?id={}".format(
        public_profile_url_base, CANONICAL_MARKETPLACE_PROFILE
    )
    response = requests.get(public_profile_url)
    page_content = response.content
    page_soup = BeautifulSoup(page_content, features="html.parser")
    page_link_elements = page_soup.select("div.pagination-bar ul.pagination li a")
    page_links = set()
    for page_link_element in page_link_elements:
        href = page_link_element.get("href", None)
        if href:
            page_links.add("{}{}".format(public_profile_url_base, href))

    def scrape_marketplace(marketplace_url):
        page_count = ""
        page_count_regex = r".*?page=(?P<page_count>\d?)"
        match = re.match(page_count_regex, marketplace_url)

        if match:
            attrs = match.groupdict()
            page_count = attrs.get("page_count", None)

        response = requests.get(marketplace_url)
        page_content = response.content
        page_soup = BeautifulSoup(page_content, features="html.parser")
        product_elements = page_soup.select(
            "div.vendor-products article.products div.col-xs-10"
        )
        products = []
        product_order = (int(page_count) * 10) - 10
        product_in_page_order = 0
        for product_element in product_elements:
            product_order = product_order + 1
            product_in_page_order = product_in_page_order + 1

            product_title_element = product_element.select_one("div.row h1")
            product_title = (
                product_title_element.get_text().strip()
                if product_title_element
                else ""
            )

            product_version_element = product_element.select_one(
                "ul.info li:nth-child(1)"
            )
            product_version = (
                product_version_element.get_text().strip()
                if product_version_element
                else ""
            )

            product_pricing_element = product_element.select_one("p.pricing span.price")
            product_pricing = (
                product_pricing_element.get_text().strip()
                if product_pricing_element
                else ""
            )

            product_info_element = product_element.select_one("p.delivery")
            product_info = (
                product_info_element.get_text().strip() if product_info_element else ""
            )

            product_description_element = product_element.select_one("p.description")
            product_description = (
                product_description_element.get_text().strip()
                if product_description_element
                else ""
            )

            # Get more detailed information on this listing
            marketplace_url_element = product_title_element.select_one("a")
            marketplace_url = marketplace_url_element.get("href")
            listing_response = requests.get(
                "https://aws.amazon.com{}".format(marketplace_url)
            )
            listing_page_content = listing_response.content
            listing_page_soup = BeautifulSoup(
                listing_page_content, features="html.parser"
            )
            fullfillment_options_element = listing_page_soup.select_one(
                "div.pdp-attributes div.fulfillment-options ul li:nth-child(1)"
            )
            fullfillment_options = (
                fullfillment_options_element.get_text().strip()
                if fullfillment_options_element
                else ""
            )

            release_version = ""
            serial = ""
            version_regex = (
                r".*?(?P<release_version>\d\d\.\d\d?)"
                r".*?(?P<serial>\d\d\d\d\d\d\d\d(\.\d{1,2})?).*?"
            )

            match = re.match(version_regex, product_version)

            if match:
                attrs = match.groupdict()
                release_version = attrs.get("release_version", None)
                serial = attrs.get("serial", None)

            product_unique_identifier = "{} ({}) - {}".format(
                product_title, fullfillment_options, serial
            )
            product = {
                "unique_identifier": product_unique_identifier,
                "version": product_version,
                "release_version": release_version,
                "title": product_title,
                "pricing": product_pricing,
                "info": product_info,
                "description": product_description,
                "product_in_page_order": product_in_page_order,
                "page_order": page_count,
                "product_order": product_order,
                "serial": serial,
                "marketplace_url":
                    "https://aws.amazon.com{}".format(marketplace_url),
                "type": fullfillment_options,
            }
            products.append(product)
        return (page_count, products)

    parallel_products = Parallel(n_jobs=-1)(
        delayed(scrape_marketplace)(page_link) for page_link in page_links
    )
    sorted_parallel_products = sorted(parallel_products, key=lambda tup: tup[0])
    print("Public profile URL: {}".format(public_profile_url))
    for page, products_per_page in sorted_parallel_products:
        for product in products_per_page:
            print(
                "\n{}\n\t\t"
                "Release: {}\n\t\t"
                "Serial: {}\n\t\t"
                "Version: {}\n\t\t"
                "Type: {}\n\t\t"
                "Page: {} \n\t\t"
                "Slot: {} \n\t\t"
                "Title: {}\n\t\t"
                "Description: \n\t\t\t\t{}\n\t\t"
                "URL: {}\n\t\t".format(
                    product["unique_identifier"],
                    product["release_version"],
                    product["serial"],
                    product["version"],
                    product["type"],
                    product["page_order"],
                    product["product_order"],
                    product["title"],
                    product["description"].replace("\n", "\n\t\t\t\t"),
                    product["marketplace_url"],
                )

            )


@click.group()
def main():
    pass


main.add_command(quicklaunch)
main.add_command(marketplace)

if __name__ == "__main__":
    sys.exit(main())
