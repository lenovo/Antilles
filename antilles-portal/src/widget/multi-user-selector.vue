<style>
.multi-user-selector{
    display:inline-block;
}
.multi-user-selector .el-input{
    width: 300px;
}
</style>

<template>
    <div class="multi-user-selector">
        <el-input readonly class="select-result-input" :placeholder="$t(allable?'Multi.User.All':'Multi.User.PleaseSelect')" :value="result"></el-input>
        <el-button @click="Select" type="primary">{{$t('Multi.User.select')}}</el-button>
        <users-selector-dialog ref="userDialog" @on-selected="onSelected" :form-value="formValue" :filter-list="filterList" :max-value="maxValue" :allable="allable || false"></users-selector-dialog>
    </div>
</template>

<script>

import UserSelectorDialog from './multi-user-selector/users-selector-dialog';
import UserGroupService from '../service/user-group'
import BillGroupService from '../service/bill-group'

export default {
    data(){
        return {
            formValue: {
                values: this.usersValue || [],
                value_type: this.usersType || 'username'
            },
            maxValue: {
                username: Number(this.usernameMax) || 50,
                usergroup: Number(this.usergroupMax) || 10,
                billinggroup: Number(this.billinggroupMax) || 10,
            },
            result: this.formatValue({values: this.usersValue,value_type: this.usersType || 'username'}),
            filterList: this.filterType.split(',')
        }
    },
    props: [
        'usersValue',
        'usersType',
        'filterType',
        'usernameMax',
        'usergroupMax',
        'billinggroupMax',
        'allable'
    ],
    components: {
        'users-selector-dialog': UserSelectorDialog
    },
    methods: {
        Select(){
            this.$refs.userDialog.init();
        },
        onSelected(res) {
            this.formValue = res;
            this.$emit('change',this.formValue);
            this.formatValue(res);
        },
        formatValue(data){
            var result;
            if(data.value_type=="billinggroup"){
                BillGroupService.getAllBillGroups().then((res)=>{
                    result = res.filter((item)=>{
                        return data.values.find((ele)=>{
                            return ele == item.id;
                        });
                    }).map((item)=>{
                        return item.name
                    }).join(',');
                    this.result = result;
                });
            }else{
                this.result = data.values.join(',');
            }
        }
    }
}
</script>
