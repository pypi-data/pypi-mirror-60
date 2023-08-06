import requests

from ddipy.verify_utils import VerifyUtils


class DatasetClient:
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                             "Chrome/54.0.2840.99 Safari/537.36"}
    baseDatasetUrl = "https://www.omicsdi.org/ws/dataset"
    mergeUrl = "https://www.omicsdi.org/ws/dataset/merge"
    getDatasetPageUrl = "https://www.omicsdi.org/ws/dataset/getDatasetPage"
    unmergeUrl = "https://www.omicsdi.org/ws/dataset/unmerge"
    getMergeCandidatesUrl = "https://www.omicsdi.org/ws/dataset/getMergeCandidates"
    multiomicsMergeUrl = "https://www.omicsdi.org/ws/dataset/multiomicsMerge"
    getAllmergedUrl = "https://www.omicsdi.org/ws/dataset/getAllmerged"
    getDatasetByUrlUrl = "https://www.omicsdi.org/ws/dataset/getDatasetByUrl"
    getAllUrl = "https://www.omicsdi.org/ws/dataset/getAll"
    getMergeCandidateCountUrl = "https://www.omicsdi.org/ws/dataset/getMergeCandidateCount"
    skipMergeUrl = "https://www.omicsdi.org/ws/dataset/skipMerge"
    getDbDatasetCountUrl = "https://www.omicsdi.org/ws/dataset/getDbDatasetCount"
    searchUrl = "https://www.omicsdi.org/ws/dataset/search"
    latestUrl = "https://www.omicsdi.org/ws/dataset/latest"
    getUrl = "https://www.omicsdi.org/ws/dataset/get"
    getSimilarByPubmedUrl = "https://www.omicsdi.org/ws/dataset/getSimilarByPubmed"
    batchUrl = "https://www.omicsdi.org/ws/dataset/batch"
    mostAccessedUrl = "https://www.omicsdi.org/ws/dataset/mostAccessed"
    getFileLinksUrl = "https://www.omicsdi.org/ws/dataset/getFileLinks"
    getSimilarUrl = "https://www.omicsdi.org/ws/dataset/getSimilar"

    def __init__(self):
        pass

    def merge(self, similar_arr, accession, database, source_url, name, access_token):
        similar_list = []
        for similar in similar_arr:
            temp_dict = {}
            temp_dict.update(accession=similar.accession)
            temp_dict.update(database=similar.database)
            temp_dict.update(sourceUrl=similar.sourceUrl)
            temp_dict.update(name=similar.name)
            similar_list.append(temp_dict)

        request_params = {
            "similars": similar_list,
            "accession": accession,
            "database": database,
            "sourceUrl": source_url,
            "name": name
        }
        tokened_header = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, "
                                        "like Gecko) "
                                        "Chrome/54.0.2840.99 Safari/537.36",
                          "x-auth-token": access_token}
        res = requests.post(self.mergeUrl, params=request_params, headers=tokened_header)
        return res

    def get_dataset_page(self, start=0, size=20):
        res = requests.get(self.getDatasetPageUrl, params={
            "start": start,
            "size": size
        }, headers=self.headers)
        return res

    # todo
    def unmerge(self, merge_candidates, access_token):
        tokened_header = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, "
                                        "like Gecko) "
                                        "Chrome/54.0.2840.99 Safari/537.36",
                          "x-auth-token": access_token}
        res = requests.post(self.unmergeUrl, params=merge_candidates, headers=tokened_header)
        return res

    def get_merge_candidates(self, start, size, access_token):
        tokened_header = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, "
                                        "like Gecko) "
                                        "Chrome/54.0.2840.99 Safari/537.36",
                          "x-auth-token": access_token}
        res = requests.get(self.getMergeCandidatesUrl, params={
            "start": start,
            "size": size
        }, headers=tokened_header)
        return res

    def multiomics_merge(self, similar_arr, accession, database, source_url, name, access_token):
        similar_list = []
        for similar in similar_arr:
            temp_dict = {}
            temp_dict.update(accession=similar.accession)
            temp_dict.update(database=similar.database)
            temp_dict.update(sourceUrl=similar.sourceUrl)
            temp_dict.update(name=similar.name)
            similar_list.append(temp_dict)

        request_params = {
            "similars": similar_list,
            "accession": accession,
            "database": database,
            "sourceUrl": source_url,
            "name": name
        }
        tokened_header = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, "
                                        "like Gecko) "
                                        "Chrome/54.0.2840.99 Safari/537.36",
                          "x-auth-token": access_token}
        res = requests.post(self.multiomicsMergeUrl, params=request_params, headers=tokened_header)
        return res

    def get_allmerged(self, access_token):
        tokened_header = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, "
                                        "like Gecko) "
                                        "Chrome/54.0.2840.99 Safari/537.36",
                          "x-auth-token": access_token}
        res = requests.get(self.getAllmergedUrl, headers=tokened_header)
        return res

    def get_dataset_by_url(self, url):

        if not url:
            return VerifyUtils.empty_param_error("url")

        res = requests.post(self.getDatasetByUrlUrl, params={
            "url": url
        }, headers=self.headers)
        return res

    def get_all(self):
        res = requests.get(self.getAllUrl, headers=self.headers)
        return res

    def get_merge_candidate_count(self, access_token):
        tokened_header = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, "
                                        "like Gecko) "
                                        "Chrome/54.0.2840.99 Safari/537.36",
                          "x-auth-token": access_token}
        res = requests.get(self.getMergeCandidateCountUrl, headers=tokened_header)
        return res

    def skip_merge(self, similar_arr, accession, database, source_url, name, access_token):
        similar_list = []
        for similar in similar_arr:
            temp_dict = {}
            temp_dict.update(accession=similar.accession)
            temp_dict.update(database=similar.database)
            temp_dict.update(sourceUrl=similar.sourceUrl)
            temp_dict.update(name=similar.name)
            similar_list.append(temp_dict)

        request_params = {
            "similars": similar_list,
            "accession": accession,
            "database": database,
            "sourceUrl": source_url,
            "name": name
        }
        tokened_header = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, "
                                        "like Gecko) "
                                        "Chrome/54.0.2840.99 Safari/537.36",
                          "x-auth-token": access_token}
        res = requests.post(self.skipMergeUrl, params=request_params, headers=tokened_header)
        return res

    def get_dataset_details(self, domain, accession, debug=False):
        if not domain:
            return VerifyUtils.empty_param_error("domain")

        if not accession:
            return VerifyUtils.empty_param_error("accession")

        res = requests.get(self.baseDatasetUrl + "/" + domain + "/" + accession, params={
            "debug": debug
        }, headers=self.headers)
        return res

    def get_dataset_files(self, domain, accession, position):
        if not domain:
            return VerifyUtils.empty_param_error("domain")

        if not accession:
            return VerifyUtils.empty_param_error("accession")

        if not position:
            return VerifyUtils.empty_param_error("position")

        res = requests.get(self.baseDatasetUrl + "/" + domain + "/" + accession + "/files",
                           params={
                               "position": position
                           },
                           headers=self.headers)
        return res

    def get_db_dataset_count(self):
        res = requests.get(self.getDbDatasetCountUrl, headers=self.headers)
        return res

    def search(self, query="", sortfield="", order="", start=0, size=20, faceCount=20):
        params = {
            "start": start,
            "size": size,
            "faceCount": faceCount
        }
        print(query)
        if not query:
            return VerifyUtils.empty_param_error("query")
        else:
            params.update(query=query)
        if not query:
            return VerifyUtils.empty_param_error("sortfield")
        else:
            params.update(sortfield=sortfield)
        if not query:
            return VerifyUtils.empty_param_error("order")
        else:
            params.update(order=order)

        res = requests.get(self.searchUrl, params=params, headers=self.headers)
        return res

    def latest(self, size=20):
        res = requests.get(self.latestUrl, params={
            "size": size
        }, headers=self.headers)
        return res

    def get(self, acc, database):
        if not acc:
            return VerifyUtils.empty_param_error("acc")

        if not database:
            return VerifyUtils.empty_param_error("database")

        res = requests.get(self.getUrl, params={
            "acc": acc,
            "database": database
        }, headers=self.headers)
        return res

    def get_similar_by_pubmed(self, pubmed):
        if not pubmed:
            return VerifyUtils.empty_param_error("pubmed")

        res = requests.get(self.getSimilarByPubmedUrl, params={
            "pubmed": pubmed
        }, headers=self.headers)
        return res

    def batch(self, acc, database):
        if not acc:
            return VerifyUtils.empty_param_error("acc")

        if not database:
            return VerifyUtils.empty_param_error("database")

        res = requests.get(self.batchUrl, params={
            "acc": acc,
            "database": database
        }, headers=self.headers)
        return res

    def most_accessed(self, size=20):
        res = requests.get(self.mostAccessedUrl, params={
            "size": size
        }, headers=self.headers)
        return res

    def get_file_links(self, acc, database):
        if not acc:
            return VerifyUtils.empty_param_error("acc")

        if not database:
            return VerifyUtils.empty_param_error("database")

        res = requests.get(self.getFileLinksUrl, params={
            "acc": acc,
            "database": database
        }, headers=self.headers)
        return res

    def get_similar(self, acc, database):
        if not acc:
            return VerifyUtils.empty_param_error("acc")

        if not database:
            return VerifyUtils.empty_param_error("database")

        res = requests.get(self.getSimilarUrl, params={
            "acc": acc,
            "database": database
        }, headers=self.headers)
        return res


if __name__ == '__main__':
    client = DatasetClient()
    res = client.search("human")
    print(res)
