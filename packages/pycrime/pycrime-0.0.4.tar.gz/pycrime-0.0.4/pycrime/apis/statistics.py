from baseapi.apis import GraphqlApi


locality_statistics_query = '''
  query localityStatistics($postcode: String!) {
    localityStatistics(postcode: $postcode) {
      localityTheftRate,
      stateTheftRate,
      theftStateAnomaly
    }
  }
'''


class StatisticsApi(GraphqlApi):
    @GraphqlApi.expose_method
    def locality_statistics(self, postcode):
        return self.perform_query(
            locality_statistics_query,
            {
                'postcode': postcode
            }
        )['localityStatistics']
