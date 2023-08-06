from datahen import API

def get(scraper_name, page_number = 1, per_page = 100, job_id = None):
  # TODO: support for non-current job 
  client = API.BaseClient()

  return client.get(f"/scrapers/{scraper_name}/current_job/pages", {'p': page_number, 'pp': per_page})