window.onload=function(){

    var baseURL = 'localhost:8099';
    var stockGridComponent;
    var topTenResults = [];
    var modelKeys = [];
    var messageHeader = 'BSE Top Stock*'
    var topStockDisclaimer = '* Top stocks are determined by calculating difference between close and open price. The maximum is the difference, higher is the rank'

    function isEmpty(val){
        return (val === undefined || val == null || val.length <= 0) ? true : false;
    }

    // register the grid component
    Vue.component('stock-grid', {
      template: '#grid-template',
      props: {
        data: Array,
        columns: Array,
      },
      data: function () {
        
        var sortOrders = {}
        this.columns.forEach(function (key) {
          sortOrders[key] = 1
        })
        
        return {
          keyword: '',
          searchMode: false,
          disclaimer: topStockDisclaimer,
          message: messageHeader,
          results: this.data,
          sortKey: '',
          sortOrders: sortOrders
        }
      },
      computed: {
        filteredData: {
            get: function () {
                var sortKey = this.sortKey
                var order = this.sortOrders[sortKey] || 1
                var data = this.results
                if (sortKey) {
                    data = data.slice().sort(function (a, b) {
                        a = a[sortKey]
                        b = b[sortKey]
                        return (a === b ? 0 : a > b ? 1 : -1) * order
                    })
                }
                return data
            }
        }
      },
      filters: {
        capitalize: function (str) {
          return str.charAt(0).toUpperCase() + str.slice(1)
        }
      },
      methods: {
        sortBy: function (key) {
          this.sortKey = key
          this.sortOrders[key] = this.sortOrders[key] * -1
        },
        home: function() {
            this.keyword = ''
            this.results = topTenResults
            this.message = messageHeader
            this.searchMode = false
        },
        search: function() {
            var that = this;
            if(!isEmpty(this.keyword)) {
                this.searchMode = true
                axios.get('http://' +  baseURL + '/search?keyword=' + this.keyword).then(function (response) {
                    console.log("Got search results for key word: " + that.keyword)
                    that.message = 'Search Results for ' + that.keyword
                    that.results = response.data
                }).catch(function (error) {
                    alert("Record not found with keyword " + that.keyword)
                    that.home()
                });
            } else {
                this.home()
            }
        }
      }
    })
 
    // Make a request to get top 10 results
    axios.get('http://' + baseURL +'/').then(function (response) {
        topTenResults = response.data || []
        var modelKeys = []
        if(topTenResults.length > 0) {
            modelKeys = Object.keys(topTenResults[0])
        }
        stockGridComponent = new Vue({
            el: '#stockApp',
            data: {
                gridColumns: modelKeys,
                gridData: topTenResults
            }
        })
    }).catch(function (error) {
        console.log(error);
    });
}