from bs4 import BeautifulSoup
import json
import requests
import hashlib


def crawl_active_airdrops(url):
    req = requests.get(url)
    soup = BeautifulSoup(req.text, "html.parser")
    airdrop_html_tag = str(soup.find()).split("\n")[-1]
    participated_list = []
    winners_list = []
    airdrop_amount_list = []
    list_of_urls = []
    deadlines_list = []
    unique_list = []
    titles_list = []
    airdrop_name_list = []
    num_of_ongoing_airdrops = int(
        airdrop_html_tag.split("href=\"/airdrop/ongoing/\">View all ")[1].split(" ongoing Airdrops")[0])
    list_of_currencies = airdrop_html_tag.split("/currencies")
    list_of_number_of_winners = airdrop_html_tag.split(
        "<p class=\"sc-1eb5slv-0 hykWbK\" color=\"text\" ")
    list_of_deadlines = airdrop_html_tag.split("<div class=\"sc-1sea04z-1 iUYxtq\">")
    list_of_titles = airdrop_html_tag.split(",\"projectName")
    list_of_airdrops = airdrop_html_tag.split("style=\"white-space:break-spaces\"")
    for url in list_of_currencies[2:]:
        currency = url.split("/")[1].split("\"><img")[0]
        if currency not in list_of_urls and len(list_of_urls) < num_of_ongoing_airdrops:
            list_of_urls.append(currency)
    for i in range(len(list_of_urls)):
        list_of_urls[i] = "https://coinmarketcap.com/currencies/" + list_of_urls[i] + "/airdrop/"
    counter = 0
    for number_of_winners in list_of_number_of_winners[1:]:
        if len(winners_list) < 3 * num_of_ongoing_airdrops + 1:
            current_item = number_of_winners.split("font-size=\"1\">")[1].split("</p>")[0]
            if counter % 3 == 0:
                participated_list.append(current_item)
            elif counter % 3 == 1:
                winners_list.append(current_item)
            elif "<span>" in current_item:
                airdrop_amount_list.append(current_item.split("<span>")[1].split("<img class")[0])
            else:
                airdrop_amount_list.append(current_item)
            counter += 1
    participated_list = participated_list[:9]
    winners_list = winners_list[:9]
    airdrop_amount_list = airdrop_amount_list[:9]
    for deadline in list_of_deadlines[1:]:
        if len(deadlines_list) < num_of_ongoing_airdrops:
            deadlines_list.append(deadline.split("<div>")[1].split("</div>")[0] + " " +
                                  deadline.split("</div><div style=\"line-height:1\">")[1].split("</div></div></td>")[
                                      0])
            unique_list.append(hashlib.md5((list_of_urls[len(deadlines_list) - 1] + " " +
                                            deadline.split("</div><div style=\"line-height:1\">")[1].split(
                                                "</div></div></td>")[0]).encode()).hexdigest())

    # for item in unique_list:
    #     print(item)
    for title in list_of_titles[1:]:
        if len(titles_list) < num_of_ongoing_airdrops:
            titles_list.append(title.split("\":\"")[1].split("\",\"")[0])

    for airdrop_name in list_of_airdrops[1:]:
        if len(airdrop_name_list) < num_of_ongoing_airdrops:
            airdrop_name_list.append(airdrop_name.split(">")[1].split("</span")[0])

    # for item in airdrop_name_list:
    #     print(item)

    return list_of_urls, participated_list, winners_list, airdrop_amount_list, deadlines_list, titles_list, airdrop_name_list, unique_list


if __name__ == '__main__':
    list_of_urls, participated_list, winners_list, airdrop_amount_list, deadlines_list, titles_list, airdrop_name_list, unique_list = crawl_active_airdrops(
        "https://coinmarketcap.com/airdrop/")
    url = "http://130.185.120.29:5200/add_info"
    for i in range(len(list_of_urls)):
        # print(airdrop_name_list[i])
        # print(titles_list[i])
        # print(participated_list[i])
        # print(winners_list[i])
        # print(airdrop_amount_list[i])
        # print(deadlines_list[i])
        # print(unique_list[i])
        # print("*********************************************************************************************")
        payload_dict = {"status": "OK", "error": "", "airdrop_name": str(
            airdrop_name_list[i]), "title": titles_list[i].encode().decode("utf-8"), "body": str(
            "number of participated : " + str(participated_list[i]) + "\n" + "number of winners : " + str(
                winners_list[i]) + "\n" + "Total amount of airdrop : " + str(
                airdrop_amount_list[i]) + "\n" + "deadline : " + str(
                deadlines_list[i]) + "\n" + "url of main page : " + str(list_of_urls[i])),
                        "unique_id": unique_list[i]}
        with open('payload.json', 'w') as fp:
            json.dump(payload_dict, fp)

        headers = {"content-type": "application/json"}
        response = requests.request("POST", url, headers=headers, data=open('payload.json', 'rb'))

        print(response.text)
