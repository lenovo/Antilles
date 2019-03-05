<template>
<composite-form-dialog ref="innerDialog"
  :title="title" size="500px"
  :form-model="operateForm"
  :form-rules="operateRules"
  :successMessageFormatter="successMessageFormatter"
  :errorMessageFormatter="errorMessageFormatter">
  <el-form-item :label="$t('BillGroup.Name')" prop="billGroupName">
    <form-value-displayer id="tid_account-operate-billgroup-name" :value="operateForm.billGroupName" />
  </el-form-item>
  <el-form-item :label="$t('BillGroup.AccountBalance')" prop="balance">
    <form-value-displayer id="tid_account-operate-billgroup-balance" :value="formatMoney(operateForm.balance)" />
  </el-form-item>
  <el-form-item :label="$t('BillGroup.AccountOperate')" prop="operate">
    <el-select id="tid_account-operate-operate" v-model="operateForm.operate">
      <el-option key="deposit" :label="$t('BillGroup.AccountOperate.Deposit')" value="deposit" />
      <el-option key="withdraw" :label="$t('BillGroup.AccountOperate.Withdraw')" value="withdraw" />
    </el-select>
  </el-form-item>
  <el-form-item :label="$t('BillGroup.AccountOperate.Amount')" prop="amount">
    <el-input id="tid_account-operate-amount" v-model="operateForm.amount">
      <template slot="prepend">{{currency}}</template>
    </el-input>
  </el-form-item>
</composite-form-dialog>
</template>
<script>
import BillGroupService from '../../service/bill-group'
import CompositeFormDialog from '../../component/composite-form-dialog'
import FormValueDisplayer from '../../component/form-value-displayer'
import ValidRoleFactory from '../../common/valid-role-factory'
import Format from '../../common/format'

export default {
  data() {
    return {
      currency: this.$store.getters['settings/getCurrency'],
      title: '',
      billGroupId: 0,
      operateForm: {
        billGroupName: '',
        balance: 1.00,
        operate: 'deposit',
        amount: '0.00'
      },
      operateRules: {
        amount: [
          ValidRoleFactory.getRequireRoleForText(this.$t('BillGroup.AccountOperate.Amount')),
          ValidRoleFactory.getValidNumberRoleForText(this.$t('BillGroup.AccountOperate.Amount')),
          ValidRoleFactory.getNumberRangeRoleForText(this.$t('BillGroup.AccountOperate.Amount'), 0.01, 99999999.99),
          ValidRoleFactory.getNumberDecimalRoleForText(this.$t('BillGroup.AccountOperate.Amount'), 2)
        ]
      },
      formatMoney: Format.formatMoney
    };
  },
  components: {
    'composite-form-dialog': CompositeFormDialog,
    'form-value-displayer': FormValueDisplayer
  },
  methods: {
    submitForm() {
      var changeAmount = 0;
      if(this.operateForm.operate == 'deposit') {
        changeAmount = this.operateForm.amount;
      }
      if(this.operateForm.operate == 'withdraw') {
        changeAmount = -1 * this.operateForm.amount;
      }
      return BillGroupService.operateAccount(this.billGroupId, Number(changeAmount));
    },
    successMessageFormatter(res) {
      var billGroup = res;
      return this.$t('BillGroup.AccountOperate.Success', {'name': billGroup.name});
    },
    errorMessageFormatter(res) {
      var errMsg = res;
      return this.$t(errMsg);
    },
    doOperate(billGroup) {
      this.mode = 'edit';
      this.billGroupId = billGroup.id;
      this.operateForm = {
        billGroupName: billGroup.name,
        balance: billGroup.accountBalance,
        operate: 'deposit',
        amount: '0.00'
      };
      this.title = this.$t('BillGroup.AccountOperate.Title', {id: billGroup.id});
      return this.$refs.innerDialog.popup(this.submitForm);
    }
  }
}
</script>
