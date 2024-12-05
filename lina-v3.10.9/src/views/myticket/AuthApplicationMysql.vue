<template>
  <div class="app-container">
    <div class="filter-container">
      <el-form ref="listQuery" :inline="true" :model="listQuery" :rules="rules" label-width="100px" class="demo-ruleForm">
        <el-form-item label="IP地址:" label-width="85px" prop="ip">
          <el-input v-model="listQuery.ip" placeholder="IP地址" style="width: 200px" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="submitForm('listQuery')">查询</el-button>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="dialogTableVisible = true">申请权限</el-button>
        </el-form-item>
      </el-form>
    </div>
    <el-dialog :visible.sync="dialogTableVisible" title="申请权限">
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
              <!-- </el-option> -->
            </el-select>
          </template>
        </el-table-column>
      </el-table>
      <!-- <div>
        {{ multipleSelection }}
      </div> -->
      <div slot="footer" class="dialog-footer">

        <el-button v-if="multipleSelection.length > 0" type="primary" @click="permissionSelect">提交</el-button>
        <!-- <el-button type="primary" @click="permissionOrdinary">普通权限</el-button> -->
        <el-button v-else type="primary" disabled>提交</el-button>
      </div>
    </el-dialog>

    <el-table
      :key="tableKey"
      v-loading="listLoading"
      :data="list"
      element-loading-text="Loading"
      border
      stripe
      fit
      highlight-current-row
      @selection-change="handleSelectionChange"
    >
      <el-table-column align="center" type="selection" width="55" />
      <el-table-column align="center" label="名称" min-width="100px">
        <template slot-scope="scope">
          {{ scope.row.name }}
        </template>
      </el-table-column>
      <el-table-column align="center" label="IP地址" min-width="100px">
        <template slot-scope="scope">
          {{ scope.row.address }}
        </template>
      </el-table-column>
      <el-table-column align="center" label="平台" min-width="50px">
        <template slot-scope="scope">
          {{ scope.row.platform }}
        </template>
      </el-table-column>
      <el-table-column align="center" label="创建者" min-width="100px">
        <template slot-scope="scope">
          {{ scope.row.created_by }}
        </template>
      </el-table-column>
    </el-table>

    <pagination v-show="total>0" :total="total" :page.sync="listQuery.page" :limit.sync="listQuery.limit" @pagination="fetchData" />

  </div>
</template>

<script>
import { getAllAssets } from '@/api/getallassets'
import { permAppDb } from '@/api/permissionApplication'
import { getProfile } from '@/api/users'
import Pagination from '@/components/Pagination'
import elDragDialog from '@/directive/el-drag-dialog' // base on element-ui

export default {
  components: {
    Pagination
  },
  directives: { elDragDialog },
  data() {
    return {
      dialogTableVisible: false,
      listLoading: false,
      tableKey: 0,
      list: null,
      total: 0,
      adminPermQuery: {
        pname: '',
        uname: '',
        nameid: ''
      },
      listQuery: {
        assettype: 'mysql',
        uname: '',
        page: 1,
        limit: 10,
        ip: '',
        sort: '+id'
      },
      // ruleForm: {
      //   ip: ''
      // },
      rules: {
        ip: [
          { required: false, message: '请输入查询的ip', trigger: 'blur' }
        ]
      },
      multipleSelection: [],
      options: [{
        value: '选项1',
        label: '黄金糕'
      },
      {
        value: '选项2',
        label: '测试蛋糕'
      }],
      value1: []
    }
  },
  created() {
    this.fetchData()
  },
  methods: {
    fetchData() {
      getProfile().then(response => {
        // console.log(response, 'ccccccc')
        this.adminPermQuery.pname = response.name
        this.adminPermQuery.uname = response.username
        this.adminPermQuery.nameid = response.id
        this.listQuery.uname = response.username

        // 要先获取到了用户名，然后再发送请求
        getAllAssets(this.listQuery).then(response => {
          this.list = response.data.items
          this.total = response.data.total
        })
      })
    },
    submitForm(listQuery) {
      this.$refs[listQuery].validate((valid) => {
        if (valid) {
          // console.log(this.ruleForm)
          this.listLoading = true
          getAllAssets(this.listQuery).then(response => {
            this.list = response.data.items
            this.total = response.data.total

            setTimeout(() => {
              this.listLoading = false
            }, 1 * 1000)
          })
        }
      })
    },
    handleSelectionChange(val) {
      this.multipleSelection = val
    },
    permissionSelect() {
      // console.log(this.multipleSelection)
      // console.log(this.adminPerm)
      this.listLoading = true
      permAppDb(this.adminPermQuery, this.multipleSelection).then(response => {
        this.openPrompt(response)

        setTimeout(() => {
          this.listLoading = false
        }, 1 * 1000)
      })
      this.dialogTableVisible = false
    },
    openPrompt(response) {
      if (response.code === 20000) {
        this.$message.success(response.mes)
      } else {
        this.$message.error(response.mes)
      }
    }
  }
}
</script>

<style scoped>

</style>
