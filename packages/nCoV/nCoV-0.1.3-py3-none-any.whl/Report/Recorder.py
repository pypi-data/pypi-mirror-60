from bs4 import BeautifulSoup
import urllib.request
import click
import os

rootUrl = 'http://3g.dxy.cn/newh5/view/pneumonia'


def lookup():
    while True:
        try:
            html = urllib.request.urlopen(rootUrl)
            bs = BeautifulSoup(html, features='html.parser')
        except Exception:
            click.clear()
            click.echo(click.style('Internet Connection ERROR!', blink=True, fg='red'))
            click.echo(click.style('Retry? [y/n]', fg='blue'))
            choice = str(input())
            if choice == 'y' or choice == 'Y':
                continue
            else:
                exit(0)

        div = bs.find('div', {'class': 'mapTop___2VZCl'})
        title = div.find_all('p')[0].find('span').text
        body = div.find_all('p')[1].find('span').text
        punctuation = str(title).split(' ')[1:3]
        punctuation[1] = punctuation[1][:5]
        punctuation = punctuation[0] + ' ' + punctuation[1]
        data = str(body).split(' ')
        confirmed = data[1]
        suspect = data[4]
        healed = data[10]
        death = data[7]

        return punctuation, confirmed, suspect, healed, death


def detailed_info():
    while True:
        try:
            html = urllib.request.urlopen(rootUrl)
            bs = BeautifulSoup(html, features='html.parser')
        except Exception:
            click.clear()
            click.echo(click.style('Internet Connection ERROR!', blink=True, fg='red'))
            click.echo(click.style('Retry? [y/n]', fg='blue'))
            choice = str(input())
            if choice == 'y' or choice == 'Y':
                continue
            else:
                exit(0)
        script = str(bs.find('script', {'id': 'getAreaStat'}).text)
        data = script[27:-11]
        # print(os.getcwd())

        with open('temp.py', 'w+') as f:
            f.write('# coding=utf-8\n')
            f.write('import pickle\n')
            f.write('import os\n')
            f.write('a = ')
            f.write(data)
            f.write('\n')
            f.write('with open(\'data.pickle\', \'wb+\') as file:\n')
            f.write('    ')
            f.write('pickle.dump(a, file, 0)\n')
            # f.write('os.system(\'python3 Report/Parser.py\')')
        os.system('python3 temp.py')
        import Report.Parser
        os.system('rm -rf temp.py data.pickle')
        exit(0)

