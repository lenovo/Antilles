<template>
<composite-form-dialog ref="innerDialog"
  :title="title" size="500px"
  :form-model="billGroupForm"
  :form-rules="billGroupRules"
  :successMessageFormatter="successMessageFormatter"
  :errorMessageFormatter="errorMessageFormatter">
  <el-form-item :label="$t('BillGroup.Name')" prop="name">
    <el-input id="tid_billgroup-name" v-model="billGroupForm.name" :disabled="mode == 'delete'"></el-input>
  </el-form-item>
  <el-form-item :label="$t('BillGroup.ChargeRate')" prop="chargeRate">
    <el-input id="tid_billgroup-charge-rate" v-model="billGroupForm.chargeRate" :disabled="mode == 'delete'">
      <template slot="prepend">{{currency}}</template>
      <template slot="append">{{$t('BillGroup.ChargeRate.Unit')}}</template>
    </el-input>
  </el-form-item>
  <el-form-item :label="$t('BillGroup.AccountInitAmount')" prop="accountInitAmount" v-if="mode == 'create'">
    <el-input id="tid_billgroup-init-amount" v-model="billGroupForm.accountInitAmount">
      <template slot="prepend">{{currency}}</template>
    </el-input>
  </el-form-item>
  <el-form-item :label="$t('BillGroup.Description')" prop="description">
    <el-input id="tid_billgroup-description" type="textarea" v-model="billGroupForm.description" :disabled="mode == 'delete'"></el-input>
  </el-form-item>
</composite-form-dialog>
</template>
<script>
import BillGroupService from '../../service/bill-group'
import CompositeFormDialog from '../../component/composite-form-dialog'
import ValidRoleFactory from '../../common/valid-role-factory'

export default {
  data() {
    return {
      currency: this.$store.getters['settings/getCurrency'],
      title: '',
      mode: '',
      billGroupId: 0,
      billGroupForm: {
        name: '',
        chargeRate: '1.00',
        accountInitAmount: '0.00',
        description: ''
      },
      billGroupRules: {
        name: [
          ValidRoleFactory.getRequireRoleForText(this.$t('BillGroup.Name')),
          ValidRoleFactory.getLengthRoleForText(this.$t('BillGroup.Name'), 3, 20),
          ValidRoleFactory.getValidIdentityNameRoleForText(this.$t('BillGroup.Name'))
        ],
        chargeRate: [
          ValidRoleFactory.getRequireRoleForText(this.$t('BillGroup.ChargeRate')),
          ValidRoleFactory.getValidNumberRoleForText(this.$t('BillGroup.ChargeRate')),
          ValidRoleFactory.getNumberRangeRoleForText(this.$t('BillGroup.ChargeRate'), 0.01, 999999.99),
          ValidRoleFactory.getNumberDecimalRoleForText(this.$t('BillGroup.ChargeRate'), 2)
        ],
        accountInitAmount: [
          ValidRoleFactory.getRequireRoleForText(this.$t('BillGroup.AccountInitAmount')),
          ValidRoleFactory.getValidNumberRoleForText(this.$t('BillGroup.AccountInitAmount')),
          ValidRoleFactory.getNumberRangeRoleForText(this.$t('BillGroup.AccountInitAmount'), 0, 99999999.99),
          ValidRoleFactory.getNumberDecimalRoleForText(this.$t('BillGroup.AccountInitAmount'), 2)
        ],
        description: [
          ValidRoleFactory.getLengthRoleForText(this.$t('BillGroup.Description'), 0, 200)
        ]
      }
    };
  },
  components: {
    'composite-form-dialog': CompositeFormDialog
  },
  methods: {
    submitForm() {
      if(this.mode == 'create') {
        return BillGroupService.createBillGroup(this.billGroupForm.name, parseFloat(this.billGroupForm.chargeRate), parseFloat(this.billGroupForm.accountInitAmount), this.billGroupForm.description);
      }
      if(this.mode == 'edit') {
        return BillGroupService.updateBillGroup(this.billGroupId, this.billGroupForm.name, parseFloat(this.billGroupForm.chargeRate), this.billGroupForm.description);
      }
      if(this.mode == 'delete') {
        return BillGroupService.deleteBillGroup(this.billGroupId);
      }
    },
    successMessageFormatter(res) {
      var billGroup = res;
      if(this.mode == 'create') {
        return this.$t('BillGroup.Create.Success', {'name': billGroup.name});
      }
      if(this.mode == 'edit') {
        return this.$t('BillGroup.Edit.Success', {'name': billGroup.name});
      }
      if(this.mode == 'delete') {
        return this.$t('BillGroup.Delete.Success', {'name': this.billGroupForm.name});
      }
    },
    errorMessageFormatter(res) {
      var errMsg = res;
      return this.$t(errMsg);
    },
    doCreate() {
      this.mode = 'create';
      this.billGroupId = 0;
      this.billGroupForm = {
        name: '',
        chargeRate: '1.00',
        accountInitAmount: '0.00',
        description: ''
      };
      this.title = this.$t('BillGroup.Create.Title');
      return this.$refs.innerDialog.popup(this.submitForm);
    },
    doEdit(billGroup) {
      this.mode = 'edit';
      this.billGroupId = billGroup.id;
      this.billGroupForm = {
        name: billGroup.name,
        chargeRate: String(billGroup.chargeRate),
        accountInitAmount: '0.00',
        description: billGroup.description
      };
      this.title = this.$t('BillGroup.Edit.Title', {id: billGroup.id});
      return this.$refs.innerDialog.popup(this.submitForm);
    },
    doDelete(billGroup) {
      this.mode = 'delete';
      this.billGroupId = billGroup.id;
      this.billGroupForm = {
        name: billGroup.name,
        chargeRate: String(billGroup.chargeRate),
        accountInitAmount: '0.00',
        description: billGroup.description
      };
      this.title = this.$t('BillGroup.Delete.Title', {id: billGroup.id});
      return this.$refs.innerDialog.popup(this.submitForm);
    }
  }
}
</script>
