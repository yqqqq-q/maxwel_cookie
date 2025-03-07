from crawler import Crawler, CrawlDataEncoder, CrawlResults

result = CrawlResults()
result['SLURM_ARRAY_TASK_ID'] = 10
result['total_time'] = 30

print(result)