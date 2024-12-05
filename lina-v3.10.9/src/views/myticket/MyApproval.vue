<template>
  <div class="app-container">

    <el-table
      :key="tableKey"
      v-loading="listLoading"
      :data="list"
      element-loading-text="Loading"
      border
      stripe
      fit
      highlight-current-row
    >
      <el-table-column align="center" label="名称" min-width="50px">
        <template slot-scope="scope">
          {{ scope.row.name }}
        </template>
      </el-table-column>
      <el-table-column align="center" label="用户" min-width="50px">
        <template slot-scope="scope">
          {{ scope.row.pname }}
        </template>
      </el-table-column>

      <el-table-column align="center" label="服务器" min-width="200px">
        <template slot-scope="scope">
          <el-button v-if="scope.row.platform == 'MySQL'" type="primary" size="small" @click="openDialog(scope.row.allasset)">
            查看
          </el-button>
          <div v-else>{{ scope.row.assets }}</div>
        </template>
      </el-table-column>

      <el-table-column align="center" label="权限" min-width="50px">
        <template slot-scope="scope">
          {{ scope.row.accounts }}
        </template>
      </el-table-column>
      <el-table-column align="center" label="备注" min-width="50px">
        <template slot-scope="scope">
          {{ scope.row.comment }}
        </template>
      </el-table-column>
      <el-table-column align="center" label="状态" min-width="30px">
        <template slot-scope="scope">
          <el-button v-if="scope.row.is_done == 'false'" type="primary" size="small" @click="myApproval(scope.row.file_name)">审批</el-button>

          <el-button v-else type="info" size="small" disabled>已审批</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog :visible.sync="dialogTableVisible" title="数据库权限" width="800">
      <el-table :data="allasset">
        <el-table-column align="center" label="名称" min-width="50px">
          <template slot-scope="scope">
            {{ scope.row.name }}
          </template>
        </el-table-column>

        <el-table-column align="center" label="IP" min-width="50px">
          <template slot-scope="scope">
            {{ scope.row.address }}
          </template>
        </el-table-column>

        <el-table-column align="center" label="数据库" min-width="50px" show-overflow-tooltip>
          <template slot-scope="scope">
            {{ scope.row.xzstr }}
          </template>
        </el-table-column>
      </el-table>
    </el-dialog>

    <pagination v-show="total>0" :total="total" :page.sync="listQuery.page" :limit.sync="listQuery.limit" @pagination="fetchData" />

  </div>
</template>

<script>
import { myAllApplication, approvalApi } from '@/api/mytickets'
import Pagination from '@/components/Pagination'

export default {
  components: {
    Pagination
  },
  data() {
    return {
      listLoading: false,
      dialogTableVisible: false,
      allasset: [],
      tableKey: 0,
      list: null,
      total: 0,
      listQuery: {
        page: 1,
        limit: 10,
        uname: ''
      }
    }
  },
  created() {
    this.fetchData()
  },
  methods: {
    fetchData() {
      myAllApplication(this.listQuery).then(response => {
        this.list = response.data.items
        this.total = response.data.total

        setTimeout(() => {
          this.listLoading = false
        }, 1 * 1000)
      })
    },
    myApproval(file_name) {
      // console.log(file_name, 'ccccccc')
      this.listLoading = true
      approvalApi(file_name).then(response => {
        // console.log('response', 'ccccccc')
        this.openPrompt(response)

        setTimeout(() => {
          this.fetchData()
        }, 1 * 1000)
      })
    },
    openPrompt(response) {
      if (response.code === 20000) {
        this.$message.success(response.mes)
      } else {
        this.$message.error(response.mes)
      }
    },
    openDialog(allasset) {
      this.allasset = allasset

      this.dialogTableVisible = true
    }
  }
}
</script>

<style scoped>

</style>
