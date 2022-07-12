""" Pure Python command-line RSS reader."""

import argparse
import requests
import json
import sys
import logging
import datetime
import os
import shutil
import base64
import uuid
import pickle
import jsonlines
from logging import StreamHandler, Formatter
from bs4 import BeautifulSoup
from dateutil import parser
from fpdf import FPDF 


version = '4.3'


def parse_input():
    """Parse a command line input"""

    parser = argparse.ArgumentParser(prog='rss-reader', description='Pure Python command-line RSS reader.')
    parser.add_argument('source', nargs='?', default='', help ='RSS URL')
    parser.add_argument(
        '--version', action='version', help='Print version info', version='%(prog)s {}'.format(version))
    parser.add_argument('--json', help='Print result as JSON in stdout', action="store_true")
    parser.add_argument('--verbose', help='Outputs verbose status messages', action="store_true")
    parser.add_argument('--limit', type=int, help='Limit news topics if this parameter provided')
    parser.add_argument(
        '--date', type = lambda s: datetime.datetime.strptime(s, '%Y%m%d'), 
        help = 'Print result from a cash for a given date')
    parser.add_argument('--html', type=str, help='Print result to HTML file')
    parser.add_argument('--pdf', type=str, help='Print result to PDF file')

    args, rest = parser.parse_known_args()
    if rest:
        print("Error: Wrong input! Unexpected arguments: " + str(rest))
    else:
        return args


def connect(path):
    """Send a get-request and obtain a content of a response in unicode"""
    try:
        response = requests.get(url = path)
    except requests.exceptions.MissingSchema:
        print("Error: Invalid URL. Check the entered argument 'source'")
        return None
    except requests.RequestException:
        print("Error: Connection to the sourse URL failed.")
        return None
    else:
        return response


class MyFeedParser:
    """Class for a created feed-parser"""

    def __init__(self, verbose):
        if verbose:
            self.logger = logging.getLogger(__name__)
            self.logger.setLevel(logging.INFO)

            handler = StreamHandler(stream=sys.stdout)
            handler.setLevel(logging.INFO)
            handler.setFormatter(Formatter(fmt='[%(asctime)s: %(levelname)s] %(message)s'))
            self.logger.addHandler(handler)

            self.logger.info('Logging started')  

        self.feed = None
        self.news = []  # list of news articles

    @staticmethod
    def deep_parsing(link, cur_date):
        """Parse description and media content from an initial web-pages"""
        a = connect(link).text
        s = BeautifulSoup(a, "html.parser")
        meta_tag = s.find('meta', attrs={'property': 'og:description'})
        if meta_tag: 
            descr = meta_tag['content']
        else:
            descr = "No description provided"
        meta_tag_image = s.find('meta', attrs={'property': 'og:image'})
        if meta_tag_image: 
            media_url = meta_tag_image['content']
            img = connect(media_url).content  # read madia in bytes
            img_base64 = base64.b64encode(img)  # encode to base64
            img_path = os.path.join(
                os.path.abspath('cashed_img'), cur_date + '_' + str(uuid.uuid4().hex) + '.data')
        else:
            media_url = ''
            img_path = ''
            img_base64 = ''
        return [descr, media_url, img_path, img_base64]

    @staticmethod
    def news_counter(a_num, limit):
        """Fills values of parameters for each new and set news counter value"""
        if limit is not None:
            if limit < a_num:
                a_counter = limit
            else:
                a_counter = a_num
        else:
            a_counter = a_num
        return a_counter
    
    def parse(self, content, limit, verbose, source):
        """Method to parse a content of a source page"""
        if verbose:
            self.logger.info('Parsing of sourse content...')
        soup = BeautifulSoup(content, "xml")
        self.feed = soup.title.text
        articles = soup.findAll('item')
        a_num = len(articles)
        a_counter = self.news_counter(a_num, limit)
        if verbose: 
            self.logger.info('Reading news...')
        for txt in articles:
            title = txt.find('title').text
            link = txt.find('link').text
            pubdate = parser.parse(txt.find('pubDate').text)    # parses pubDate to datetime object
            cur_date = str(pubdate.date())
            # connect to link and psrse description from an initial web-page                        
            dp = self.deep_parsing(link, cur_date)
            # create an Article object for each item
            article = {
                'title': title, 'pubdate': pubdate.isoformat(), 'link': link, 'description': dp[0], 
                'media_url': dp[1], 'media_path': dp[2], 'feed': self.feed, 'source': source
                }
            # append current article to a collection of news"""
            self.news.append(article)

            # send article to cash file
            with open('dates.json', 'r') as f:
                mydates = json.load(f)
            if cur_date in mydates:
                filepath = os.path.abspath(mydates[cur_date])
                # check whether current article wasn't appended to cash before
                flag = 0
                with jsonlines.open(mydates[cur_date]) as reader:
                    for obj in reader:
                        if obj['link'] == article['link']:
                            flag = 1
                            setted_media_path = obj['media_path']
                            break
                if flag == 0:
                    with jsonlines.open(filepath, mode='a') as writer:
                        writer.write(article)
                    if article['media_url'] != '':
                        with open(article['media_path'], 'wb') as f:
                            pickle.dump(dp[3], f)
                elif article['media_url'] != '':
                    article['media_path'] = setted_media_path
            else:
                mydates[cur_date] = os.path.join(os.path.abspath('cashed_feeds'), cur_date+'.jsonl')
                with open('dates.json', 'w') as f:
                    json.dump(mydates, f) 
                with jsonlines.open(mydates[cur_date], mode='w') as writer:
                    writer.write(article)
                if article['media_url'] != '':
                    with open(article['media_path'], 'wb') as f:
                        pickle.dump(dp[3], f)

            a_counter -= 1
            if not a_counter:
                break
    
    def cash_read(self, my_date, my_source, verbose, limit):
        """Reading of cashed news"""
        with open('dates.json', 'r') as f:
            mydates = json.load(f)
        cur_date = str(my_date.date())
        if cur_date in mydates:
            if verbose:
                self.logger.info('Reading news from cash for the entered date...') 
            with jsonlines.open(mydates[cur_date]) as reader:
                if my_source != '':
                    flag = 0    # Flag to check if cashed news for entered date are available for entered feed
                    for obj in reader:
                        if obj['source'] == my_source and flag == 0:
                            self.feed = obj['feed']
                            self.news.append(obj)
                            flag = 1
                        elif obj['source'] == my_source and flag == 1:
                            self.news.append(obj)
                        if limit is not None:
                            if len(self.news) > limit:
                                self.news = self.news[len(self.news)-limit:]
                    if flag == 0: 
                        print("Error: There are no cashed news for the entered date and feed.")
                        sys.exit()
                else:
                    # read  cashed articles for the entered date for all sources
                    for obj in reader:
                        self.news.append(obj)
                    if limit is not None:
                        if len(self.news) > limit:
                            self.news = self.news[len(self.news)-limit:]
                    # create a list of feeds available for the entered date
                    list_feeds = [a['feed'] for a in self.news]
                    unique_feeds = set(list_feeds)
                    self.feed = ", ".join(unique_feeds)
                    if verbose:
                        self.logger.info('Reading of news from cash is finished')
        else:
            print("Error: There are no cashed news for the entered date.")
            sys.exit()

    def print_json(self, verbose):
        """Converts results to JSON and prints to stdout"""
        news_cut = []
        for new in self.news:
            a = {
                'title': new['title'], 'pubdate': new['pubdate'], 
                'link': new['link'], 'description': new['description']
                }
            if new['media_url'] != '':
                a['media_url'] = new['media_url']
            news_cut.append(a)
        d = {'feed': self.feed, 'news': news_cut}
        print(json.dumps(d, ensure_ascii = False, indent = 2))
        if verbose:
                self.logger.info('Printing of JSON is finished')

    def print_html(self, path, verbose):
        """Converts results to HTML file"""
        if verbose:
            self.logger.info('Creating of HTML file...')
        try:
            shutil.copy('rss_downloads.html', path)
            mypath = os.path.join(path, 'rss_downloads.html')
            with open(mypath, 'w', encoding='utf-16') as f:
                self.news.sort(key=lambda dictionary: dictionary['feed'])
                feed = self.news[0]['feed']
                a = '  <h1>' + feed + '</h1>'
                f.write(a)
                for n in self.news:
                    if n['feed'] != feed:
                        a = '  <h1>' + n['feed'] + '</h1>'
                        f.write(a)
                        feed = n['feed']
                    a = '  <h3><b>' + n['title'] + '</b></h3>'
                    a += '<p>Date: <i>' + n['pubdate'][:10] + '</i><br>'
                    a += 'Link: <a href =' + n['link'] + '>' + n['link'] + '</a><br>'
                    f.write(a)
                    if n['media_url'] != '':
                        with open(n['media_path'], 'rb') as fi:
                            data_base64 = pickle.load(fi)
                            data = data_base64.decode()    # convert bytes to string
                        img_html = '  ' + '<img src="data:image/jpeg;base64,' + data
                        img_html += '" alt="New image" height = "150"'    # embed in html
                        f.write(img_html)
                    a = '<br><br>' + n['description'] + '<br></p>'
                    f.write(a)
                f.write('</body>')
                f.write('</html>')
        except Exception as e:
            print('Error: HTML file creation failed')
        else:
            if verbose:
                self.logger.info('News are stored in a file: {}'.format(mypath))
            return True

    def print_pdf(self, path, verbose):
        """Converts results to PDF file"""
        if verbose:
            self.logger.info('Creating of PDF file...')
        try:
            mypath_pdf = os.path.join(path, 'rss_downloads.pdf')
            pdf = FPDF()
            pdf.alias_nb_pages()
            font_path = os.path.join(os.path.abspath('font'), 'DejaVuSerif.ttf')
            pdf.add_font('DejaVuSerif', '', font_path, uni=True)
            font_path = os.path.join(os.path.abspath('font'), 'DejaVuSerif-Bold.ttf')
            pdf.add_font('DejaVuSerif', 'B', font_path, uni=True)
            font_path = os.path.join(os.path.abspath('font'), 'DejaVuSerif-Italic.ttf')
            pdf.add_font('DejaVuSerif', 'I', font_path, uni=True)

            pdf.add_page()
            pdf.set_font('DejaVuSerif', 'B', 16)
            self.news.sort(key=lambda dictionary: dictionary['feed'])
            feed = self.news[0]['feed']
            pdf.cell(0, 5, feed, 0, 1)
            pdf.ln() 
            im_count = 0
            for n in self.news:
                if n['feed'] != feed:
                    pdf.set_font('DejaVuSerif', 'B', 16)
                    feed = n['feed']
                    pdf.ln()
                    pdf.cell(0, 5, feed, 0, 1)
                    pdf.ln()
                pdf.set_font('DejaVuSerif', 'B', 12)
                pdf.multi_cell(0, 5, n['title'], 0)  
                pdf.set_font('DejaVuSerif', 'I', 10)
                pdf.cell(0, 5, 'Date: '+n['pubdate'][:10], 0, 1) 
                pdf.cell(0, 5, 'Link: '+n['link'], 0, 1, '', False, n['link'])
                if n['media_url'] != '':
                    with open(n['media_path'], 'rb') as fi:
                        data_base64 = pickle.load(fi)
                        data = base64.b64decode(data_base64)    # decode from base64 (bytes)
                    with open('output-image'+str(im_count)+'.jpg', 'wb') as im:
                        im.write(data)
                    pdf.image('output-image'+str(im_count)+'.jpg', None, None, 70)
                    im_count += 1
                
                pdf.set_font('DejaVuSerif', '', 12)
                pdf.multi_cell(0, 5, n['description'], 0)
                pdf.ln()
                     
            pdf.output(mypath_pdf, 'F')
            for i in range(im_count):
                os.remove('output-image'+str(i)+'.jpg')
        except Exception as e:
            print('Error: PDF file creation failed')
        else:
            if verbose:
                self.logger.info('News are stored in a file: {}'.format(mypath_pdf))
            return True
        
    def __str__(self):
        result = '\n' + "Feed: {}".format(self.feed) + '\n' + '\n'
        for n in self.news:
            result += "Title: {}".format(n['title']) + '\n'
            result += "Date: {}".format(n['pubdate']) + '\n'
            result += "Link: {}".format(n['link']) + '\n'
            result += "Description: {}".format(n['description']) + '\n' + '\n'
        return result

    def choose_printout(self, json, html, pdf, verbose):
        """Choose formats of printout according to command line arguments"""
        if json:
            self.print_json(verbose)
            if html:
                self.print_html(html, verbose)
            elif pdf:
                self.print_pdf(pdf, verbose)
        else:
            if html:
                self.print_html(html, verbose)
            elif pdf:
                self.print_pdf(pdf, verbose)
            else:
                print(self)  
                if verbose:
                    self.logger.info('News are printed')  


def main():
    args = parse_input()  # parsing of command line input

    # create an instance of MyFeedParser class
    my_feed = MyFeedParser(args.verbose) 

    if args.date:
        my_feed.cash_read(args.date, args.source, args.verbose, args.limit)
        my_feed.choose_printout(args.json, args.html, args.pdf, args.verbose)
    else: 
        if args.source != '':
            content = connect(args.source).text     # obtain a content of source page
            if content is not None:
                my_feed.parse(content, args.limit, args.verbose, args.source) 
                my_feed.choose_printout(args.json, args.html, args.pdf, args.verbose)
            else:
                print('Error: There is no available content at this source.')
    if args.verbose:
        my_feed.logger.info('RSS-reader finished. Logging stopped')     


if __name__ == '__main__':
    main()