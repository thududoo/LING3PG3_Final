from bs4 import BeautifulSoup # type: ignore

from bs4 import XMLParsedAsHTMLWarning # type: ignore
import warnings

warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)

def remove_elements_by_class(html_content, class_name):
    """
    Removes all HTML elements with the specified class name from the given HTML content.

    Args:
        html_content: The HTML content as a string.
        class_name: The class name of the elements to remove.

    Returns:
        The modified HTML content with the elements removed.
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    for element in soup.find_all(class_=class_name):
        element.decompose()
    return str(soup)

with open("filename.txt", "r") as f:
    filenames = f.readlines()
for filename in filenames:
    with open(f"./data/{filename.strip()}", "r") as h:
        modified_html = "\n".join(h.readlines())
        modified_html = remove_elements_by_class(modified_html, "otherCountries")
        modified_html = remove_elements_by_class(modified_html, "river1")
        modified_html = remove_elements_by_class(modified_html, "river2")
        modified_html = remove_elements_by_class(modified_html, "river3")
        modified_html = remove_elements_by_class(modified_html, "lake")
        modified_html = remove_elements_by_class(modified_html, "ocean")
        with open(f"./data/{filename.strip()}_cleaned.svg", "w") as m:
            m.write(modified_html)