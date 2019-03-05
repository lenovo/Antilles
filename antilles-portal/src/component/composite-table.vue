<style>
  .composite-table-header {
    margin-bottom: 20px;
    border: 0;
  }
  .composite-table-header-span{
    margin:0 20px;
  }
  .composite-table-footer{
    padding-top: 20px;
  }
  .table-header-color:{
    color:#666;
  }
  .antilles-table-header, .antilles-table-header th {
    background: #f8f8f8 !important;
    color:#666;
    border-top:1px solid #eee;
  }
  .antilles-table-header-cell {
    font-weight: normal;
  }
</style>
<template>
  <div class="composite-table b-w p-20">
    <el-row class="composite-table-header">
      <el-col :span="19" justify="left">
        <slot name="controller"></slot>
      </el-col>
      <el-col :span="5" align="right">
        <el-input id="tid_composite-table-search"
          style="max-width: 260px;"
          v-if="searchEnable"
          :placeholder="searchPlaceholder"
          v-model="searchKeyword"
          @keyup.enter.native="onSearchEnter"
          @blur="onSearchBlur">
          <el-button slot="prepend" icon="el-icon-search"></el-button>
        </el-input>
      </el-col>
    </el-row>
    <el-row class="composite-table-body">
      <el-col :span="24">
        <el-table id="tid_composite-table-inner-table"
          stripe
          ref="innerTable"
  		    :data="innerTableData"
  		    style="width: 100%"
          header-row-class-name='antilles-table-header'
          header-cell-class-name='antilles-table-header-cell'
  		    :default-sort="defaultSort"
          @sort-change="onSortChange"
          @selection-change="onSelectionChange"
          v-loading="loading" >
          <el-table-column
            v-if="selectionEnable"
            type="selection"
            width="55">
          </el-table-column>
          <slot></slot>
        </el-table>
      </el-col>
    </el-row>
    <el-row class="composite-table-footer" v-show="pageSizes.length > 0 && pageSize > 0">
      <el-col :span="12" align="left">
        <el-pagination id="tid_composite-table-page-size"
          @size-change="onPageSizeChange"
          :current-page="innerCurrentPage"
          :page-sizes="pageSizes"
          :page-size="innerPageSize"
          layout="total, sizes"
          :total="innerTotal">
        </el-pagination>
      </el-col>
      <el-col :span="12" align="right">
        <el-pagination id="tid_composite-table-page-number"
          :disabled='innerTotal<=innerPageSize'
          @current-change="onCurrentPageChange"
          :current-page="innerCurrentPage"
          :page-sizes="pageSizes"
          :page-size="innerPageSize"
          layout="prev, pager, next, jumper"
          :total="innerTotal">
        </el-pagination>
      </el-col>
    </el-row>
  </div>
</template>
<script>
  import TableDataFetcherFactory from '../common/table-data-fetcher-factory'
  export default {
    data() {
      return {
        innerTableData: this.tableData,
        searchPlaceholder: this.$t('CompositeTable.SearchPlaceholder'),
        searchKeyword: '',
        innerPageSize: this.pageSize,
        innerCurrentPage: this.currentPage,
        innerTotal: this.total,
        innerSort: this.defaultSort,
        loading: false,
        autoRefreshInterval: 0,
        autoRefreshTimerId: 0,
        keywordCache: ''
      }
    },
    props: [
      'tableData',
      'tableDataFetcher',
      'selectionEnable',
      'defaultSort',
      'currentPage',
      'pageSizes',
      'pageSize',
      'total',
      'searchEnable',
      'searchProps',
      'externalFilter',
      'autoRefresh',
      'showErrorMessage'
    ],
    mounted() {
      this.autoRefreshInterval = this.autoRefresh;
      this.autoRefreshTimerId = 0;
      if(this.defaultSort) {
        // it will call on sort to init table data
      } else {
        this.fetchTableData(true);
      }
    },
    watch: {
      externalFilter: {
        handler: function(val, oldVal) {
          this.$nextTick(() => {
            this.fetchTableData(true);
          });
        },
        deep: true
      },
      tableData: {
        handler: function(val, oldVal) {
          this.$nextTick(() => {
            this.fetchTableData(true);
          });
        }
      },
      loading: {
        handler: function(val, oldVal) {
          this.$emit('loading-change', val);
        }
      }
    },
    beforeDestroy() {
      // Set interval to zero will stop auto refresh.
      this.autoRefreshInterval = 0;
      if(this.autoRefreshTimerId > 0) {
        clearTimeout(this.autoRefreshTimerId);
        this.autoRefreshTimerId = 0;
      }
    },
    methods: {
      onSearchBlur(val) {
        this.searchKeyword = this.keywordCache;
        window.document.onkeyup = null;
      },
      onSearchEnter() {
        let self = this;
        if(self.searchKeyword != self.keywordCache) {
          self.keywordCache = self.searchKeyword;
          self.fetchTableData(true);
          self.$emit('search-change', self.searchKeyword);
        }
      },
      onPageSizeChange(val) {
        this.innerPageSize = val;
        if(this.innerPageSize * (this.innerCurrentPage - 1) + 1 <= this.innerTotal) {
          this.fetchTableData(false);
          this.$emit('page-change', this.innerPageSize, this.innerCurrentPage);
        }
      },
      onCurrentPageChange(val) {
        this.innerCurrentPage = val;
        this.fetchTableData(false);
        this.$emit('page-change', this.innerPageSize, this.innerCurrentPage);
      },
      onSortChange(sort) {
        this.innerSort.prop = sort.prop;
        this.innerSort.order = sort.order;
        this.fetchTableData(true);
        this.$emit('sort-change', sort.prop, sort.order);
      },
      onSelectionChange(selection) {
        this.$emit('selection-change', selection);
      },
      fetchTableData(gotoStartPage, isAutoRefresh) {
        var tableDataFetcher = this.tableDataFetcher;
        if(tableDataFetcher == null && this.tableData != null) {
          tableDataFetcher = TableDataFetcherFactory.createFixLocalPagingFetcher(this.tableData);
        }
        if(tableDataFetcher) {
          var pageSize = this.innerPageSize;
          var currentPage = this.innerCurrentPage;
          if(gotoStartPage) {
            currentPage = 1;
          }
          var sort = {
            prop: this.innerSort.prop,
            order: this.innerSort.order
          };
          var filters = [];
          if(this.externalFilter) {
            var propNames = Object.getOwnPropertyNames(this.externalFilter);
            propNames.forEach((propName) => {
              if (propName != '__ob__') {
                var filterOption = {
                  prop: propName,
                  type: this.externalFilter[propName].type,
                  values: this.externalFilter[propName].values
                };
                if(this.externalFilter[propName].value_type) {
                  filterOption.value_type = this.externalFilter[propName].value_type
                }
                filters.push(filterOption);
              }
              /*
              if (propName = '__ob__') {
                return;
              }
              var filterOption = {
                prop: propName,
                type: this.externalFilter[propName].type,
                values: this.externalFilter[propName].values
              };
              filters.push(filterOption);
              */
            });
          }
          var search = null;
          if(this.searchEnable) {
            search = {
              props: this.searchProps,
              keyword: this.searchKeyword
            }
          } else {
            search = {
              props: [],
              keyword: this.searchKeyword
            }
          };
          if(isAutoRefresh) {
            // Do nothing
          } else {
            this.$nextTick(() => {
              this.loading = true;
            });
          }
          tableDataFetcher.fetch(pageSize, currentPage, sort, filters, search).then((res) => {
              this.innerTableData = res.data;
              this.innerTotal = res.total;
              this.innerPageSize = res.pageSize;
              this.innerCurrentPage = res.currentPage;
              this.$nextTick(() => {
                this.loading = false;
                this.$refs.innerTable.doLayout();
              });
              if (this.autoRefreshInterval > 0) {
                let self = this;
                if(this.autoRefreshTimerId > 0) {
                  clearTimeout(this.autoRefreshTimerId);
                }
                this.autoRefreshTimerId = setTimeout(function() {
                  self.fetchTableData(false, true);
                },this.autoRefreshInterval);
              }
            }, (errMsg, status) => {
              this.innerTableData = [];
              this.innerTotal = 0;
              this.innerPageSize = pageSize;
              this.innerCurrentPage = 1;
              if(this.showErrorMessage === false) {
                // Do nothing
              } else {
                this.$message.error(errMsg);
              }
              this.$emit('table-data-fetch-error', {'message': errMsg, 'status': tableDataFetcher.status});
              this.$nextTick(() => {
                this.loading = false;
                this.$refs.innerTable.doLayout();
              });
            });
        }
      },
      reLayout() {
        this.$refs.innerTable.doLayout();
      }
    }
  }
</script>
