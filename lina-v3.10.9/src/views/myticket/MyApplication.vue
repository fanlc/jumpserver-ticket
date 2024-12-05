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
          <el-tooltip
            v-if="scope.row.is_done == 'error'"
            class="box-item"
            effect="dark"
            content="Top Center prompts info"
            placement="top"
          >
            <el-button type="danger" size="small" disabled>错误</el-button>
          </el-tooltip>
          <el-button v-else-if="scope.row.is_done == 'true'" type="success" size="small" disabled>已审批</el-button>
          <el-button v-else type="info" size="small" disabled>未审批</el-button>
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

    <!-- <el-dialog :visible.sync="dialogTableVisible" title="申请权限">
      <el-table :data="multipleSelection">
        <el-table-column property="name" label="名称" min-width="100px" />
        <el-table-column property="address" label="Address" min-width="100px" />
        <el-table-column property="platform" label="平台" min-width="50px" />
        <el-table-column property="created_by" label="创建者" min-width="100px" />
        <el-table-column label="选择数据库" min-width="100px">
          <template slot-scope="scope">
            <el-select v-model="scope.row.xz" multiple filterable placeholder="请选择">
              <el-option
                v-for="item in scope.row.alldb"
                :key="item.value"
                :label="item.label"
                :value="item.value"
                :disabled="item.disabled"
              />
            </el-select>
          </template>
        </el-table-column>
      </el-table>
      <div slot="footer" class="dialog-footer">

        <el-button v-if="multipleSelection.length > 0" type="primary" @click="permissionSelect">提交</el-button>
        <el-button v-else type="primary" disabled>提交</el-button>
      </div>
    </el-dialog> -->

    <pagination v-show="total>0" :total="total" :page.sync="listQuery.page" :limit.sync="listQuery.limit" @pagination="fetchData" />

  </div>
</template>

<script>
import { myAllApplication } from '@/api/mytickets'
import { getProfile } from '@/api/users'
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
      ccc: '',
      total: 0,
      listQuery: {
        page: 1,
        limit: 10,
        uname: 'cccc'
      }
    }
  },
  created() {
    this.fetchData()
  },
  methods: {
    fetchData() {
      getProfile().then(response => {
        // console.log(response, 'ccccccc')
        this.listQuery.uname = response.username
        myAllApplication(this.listQuery).then(response => {
          this.list = response.data.items
          this.total = response.data.total
        })
      })
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
