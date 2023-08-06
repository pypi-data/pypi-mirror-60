from datahen import API

def all():
  client = API.BaseClient()

  return client.get('/scrapers')

def get(scraper_name):
  client = API.BaseClient()

  result = client.get(f"/scrapers/{scraper_name}")
  
  if 'message' in result and result['message'] == "dbr: not found":
    raise ValueError(f"Scraper named {scraper_name} was not found")
  else:
    return result

def get_current_job_stats(scraper_name):
  client = API.BaseClient()

  result = client.get(f"/scrapers/{scraper_name}/current_job/stats/current")
  
  if 'message' in result and result['message'] == "dbr: not found":
    raise ValueError(f"Scraper named {scraper_name} was not found or no active job is present")
  else:
    return result