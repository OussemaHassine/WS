import requests
import csv
from bs4 import BeautifulSoup

# URL of the website to scrape
base_url = "https://www.scholarshipsads.com/category/tags/tunisia/page/"

# Create a CSV file to store the results
with open("scholarships.csv", "w", newline="",encoding="utf-8") as f:
    writer = csv.writer(f)

    # Write the header row of the CSV file
    writer.writerow(["id","Title", "Ammount", "Institution", "Degree", "Field", "Students", "Location", "Deadline"])

    # Set the page number to 1
    page = 1
    id=0

    # Set a flag to indicate whether there are more pages to scrape
    more_pages = True

    # Loop until there are no more pages to scrape
    while page<20:
        # Construct the URL for the current page
        url = base_url + str(page)

        # Make a request to the website and retrieve the HTML
        html = requests.get(url).text

        # Parse the HTML with BeautifulSoup
        soup = BeautifulSoup(html, "html.parser")

        # Find all the scholarship elements on the page
        scholarships = soup.find_all("div", class_="scholarship-card")

        # Loop through each scholarship element and extract the relevant information
        for scholarship in scholarships:
            
            deadline="Not Mentioned"
            title = scholarship.find("h2").text.strip()
            print(title)
            for data in scholarship.find_all("li"):
                if data.find("i", class_="icon-dollor"):
                    ammount = data.text.strip()
                    print(ammount)
                elif data.find("i", class_="icon-place"):
                    institution = data.text.strip()
                    print(institution)
                elif data.find("i", class_="icon-Bachelor2"):
                    degree = data.text.strip()
                    print(degree)
                elif data.find("i", class_="icon-book"):
                    field = data.text.strip()
                    print(field)
                elif data.find("i", class_="icon-world"):
                    students = data.text.strip()
                    print(students)
                elif data.find("i", class_="icon-map"):
                    location = data.text.strip()
                    print(location)
                elif data.find("i", class_="icon-calendar"):
                    deadline = data.text.strip()
                    print(deadline)

            # Write the information to the CSV file
            writer.writerow([id,title, ammount, institution, degree, field, students, location, deadline])
            id=id+1

        # Check if there is a "next" button on the page
        next_button = soup.find("a", class_="next")
        if next_button:
            # If there is a next button, increment the page number and continue looping
            page += 1
        else:
            # If there is no next button, set the flag to False to stop looping
            more_pages = False

print("Done!")
