import smtplib
from email.mime.text import MIMEText

import requests
from bs4 import BeautifulSoup
from Levenshtein import distance

PRODUCT_URL = "http://products.merchantwarehouse.com/credit-card-machines/wireless-credit-card-terminals/exadigm-xd2000"
PRODUCT_IMAGE = "http://products.merchantwarehouse.com/sites/merchantwarehouse.com/files/imagecache/mw_product/ExadigmXD2000.png"
PRODUCT_SUMMARY = [
    u'The Exadigm XD2000 offers a flexible and affordable alternative to  the better known brand wireless credit card terminals. The powerful  XD2000 wireless credit card terminal delivers the highest level of  terminal security.',
    u'The XD2000 is built with Linux based software and PC Style components for the best possible flexibility and upgradeability.',
    u'The Exadigm XD2000 has the ability to process wireless transactions on several wireless networks, including GPRS and CDMA.'
]
PRODUCT_FEATURES = [
    u'Built on a PC-based architecture offering the highest degree of flexibility & upgradeability ',
    u'Linux operating system, which allows for fast and affordable software changes, updates and customization ',
    u'PC style components, such as host based USB and Serial Ports, allow for easy hardware integration ',
    u'Superior terminal security supporting up to 1024-bit SSL encryption  at the time of card swipe eliminating the need for 3rd party processing  of transactions ',
    u'CISP validated providing the most secure terminal on the market today ', u'Modular design allowing a single terminal to offer multiple communication options ',
    u'Ability to utilize every day USB devices for integration into the terminal with little or no special software changes'
]

errors = []

r = requests.get(PRODUCT_URL)

if r.status_code == 200:
    body = BeautifulSoup(r.text).body

    if not len(body('img', attrs={"src": PRODUCT_IMAGE})):
        errors.append("Image not found")
    try:
        found_summary = [p.get_text() for p in body('div', class_="pane-field-product-description")[0]('p')]
    except (IndexError, AttributeError) as e:
        errors.append("Summary not found")
    try:
        found_features = [li.get_text() for li in body('div', class_="pane-field-product-features")[0].ul('li')]
    except (IndexError, AttributeError) as e:
        errors.append("Features not found")

    if not (all(distance(a, b) < 10 for a, b in zip(found_summary, PRODUCT_SUMMARY))):
        errors.append("Summaries differ")
    if not (all(distance(a, b) < 10 for a, b in zip(found_features, PRODUCT_FEATURES))):
        errors.append("Features differ")

else:
    errors.append("Bad status: %d" % r.status_code)


if errors:
    errors.insert(0, "ERRORS DETECTED")
    msg = MIMEText('\n'.join(errors))
else:
    msg = MIMEText("NO ERRORS DETECTED")

msg['Subject'] = 'Merchant Warhouse Product Page Status'
msg['From'] = 'billm@commonplaces.com'
msg['To'] = 'billm@commonplaces.com'

s = smtplib.SMTP('localhost')
s.sendmail('billm@commonplaces.com', ['billm@commonplaces.com'], msg.as_string())
s.quit()
