from bs4 import BeautifulSoup
from bs4.element import NavigableString
from collections import Counter
import requests
import json


class Scraper():

    PARSING_LINK: str = "Who is hiring?"
    SEPARATOR: str = "_"
    BASE_URL: str = "https://news.ycombinator.com/"

    def __init__(self):
        self.keywords = {
            "python",
            "javascript",
            "java",
            "c#",
            "ruby",
            "kotlin"
        }
        pass

    def scrape(self):
        search_page = "https://news.ycombinator.com/submitted?id=whoishiring"
        response = requests.get(search_page)
        print(response.status_code)

        soup = BeautifulSoup(response.content, "html.parser")
        story_links = soup.findAll("a", {"class": "storylink"})
        post_links = []

        # Get the links for all 'Who's Hiring' posts.
        for e in story_links:
            flattened_link_contents = self.SEPARATOR.join(e.contents)  # Is a list.
            if self.PARSING_LINK.lower() in flattened_link_contents.lower():
                print(f"Found Post: {flattened_link_contents}")
                href = e.get("href")
                post_links.append(href)
        
        keyword_map = Counter()
        keyword_list = []

        # Scrape the post links.
        for link in post_links:
            job_post_map = self.scrape_hiring_submission_page(link)
            keyword_map += job_post_map
            keyword_list.append(job_post_map)

        print(f"Final map: {keyword_map}")
        
        # Output Text
        with open("output.txt", "w") as f:
            for key, count in keyword_map.items():
                f.write(f"{key}: {count}\n")

        # Output JSON
        with open("output.json", "w") as f:
            json.dump(keyword_map, f, indent=2)

        # Output Time-Series JSON
        keyword_list.reverse()
        with open("series_output.json", "w") as f:
            json.dump(keyword_list, f, indent=2)

    def scrape_hiring_submission_page(self, url: str):
        submission_url = self.BASE_URL + url
        print(f"Scraping: {submission_url}")
        response = requests.get(submission_url)
        print(response.status_code)

        soup = BeautifulSoup(response.content, "html.parser")
        job_posts = soup.findAll("span", {"class": "commtext"})
        keyword_map = Counter()

        for x in job_posts:
            keyword_map += self.scrape_job_post(x)

        print(f"submission map: {keyword_map}")
        return keyword_map

    def scrape_job_post(self, post):
        contents = post.contents
        keyword_map = Counter()

        if contents is None:
            return keyword_map

        first_element = contents[0]
        if type(first_element) is not NavigableString:
            return keyword_map

        print(f"Parsing: {type(first_element)} {first_element}")
        parsed_title_elements = first_element.split("|")
        if len(parsed_title_elements) < 3:
            # This post is probably not properly formatted, so skip.
            return keyword_map

        for content in contents:
            content_str = str(content)
            words = content_str.split(" ")
            for word in words:
                key = word.lower()
                if key in self.keywords:
                    keyword_map[key] = 1

        print(keyword_map)
        return keyword_map


if __name__ == "__main__":
    scraper = Scraper()
    scraper.scrape()