import datahen.Scrapers
import sys, argparse
import pprint

pp = pprint.PrettyPrinter(indent=1)

class DatahenCLI:
  def __init__(self):
    parser = argparse.ArgumentParser(description='Datahen python client')
    parser.add_argument('command', help='Subcommand to run')
    args = parser.parse_args(sys.argv[1:2])

    if not hasattr(self, args.command):
      print('Unrecognized command')
      parser.print_help()
      exit(1)

    getattr(self, args.command)()

  def scraper(self):
    ScraperCLI()

class ScraperCLI:
  def __init__(self):
    parser = argparse.ArgumentParser(description='Actions related to scrapers')
    parser.add_argument('action')
    args = parser.parse_args(sys.argv[2:3])

    if not hasattr(self, args.action):
      print('Unrecognized command')
      parser.print_help()
      exit(1)

    getattr(self, args.action)(args)

  def list(self, args):
    parser = argparse.ArgumentParser(description='List all scrapers on the account')
    parser.add_argument('-p', '--page', help="Page number", type=int, default=1)
    parser.add_argument('-P', '--per-page', help="Amount of records per page", type=int, default=100)
    args = parser.parse_args(sys.argv[3:])
    
    params = {
      'p': args.page,
      'pp': args.per_page
    }

    pp.pprint(datahen.Scrapers.all(params=params))

if __name__ == '__main__':
  DatahenCLI()