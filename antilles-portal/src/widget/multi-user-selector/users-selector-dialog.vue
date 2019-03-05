<template>
    <composite-form-dialog ref="innerDialog" 
    :title="$t('Multi.User.Title')" 
    size="500px" 
    :form-model="usersForm"
    :form-rules="usersRules">
        <el-form-item :label="$t('Multi.User.Filter')">
            <el-select v-model="usersForm.Filter" @change="clearState">
                <el-option v-for="item in filterList" :key="item.toString()" :label="$t('Multi.User.'+item)" :value="item"></el-option>
            </el-select>
        </el-form-item>        
        <el-form-item :label="$t('Multi.User.username')" prop="username" v-if="usersForm.Filter=='username'">
            <el-input type="textarea" 
            resize="none" 
            :placeholder="$t(allable?'Multi.User.All':'Multi.User.PleaseSelect')" 
            v-model="usersForm.username" 
            :autosize="{ minRows: 2}"></el-input>
            <el-form-item  v-show="usersForm.username">
                <el-button @click="onClearClick" type="danger" size="mini">{{$t('MultiTagsInput.Clean')}}</el-button>
            </el-form-item>
        </el-form-item>
        <el-form-item :label="$t('Multi.User.usergroup')" prop="usergroup" v-if="usersForm.Filter=='usergroup'">
            <el-select 
            v-model="usersForm.usergroup" 
            :placeholder="$t(allable?'Multi.User.All':'Multi.User.PleaseSelect')" 
            multiple 
            :multiple-limit="maxValue.usergroup">
                <el-option v-for="item in usersData.usergroup" 
                :key="item.id" 
                :value="item.name" 
                :label="item.name"></el-option>
            </el-select>
            <el-form-item  v-show="usersForm.usergroup.length>0">
                <el-button @click="onClearClick" type="danger" size="mini">{{$t('MultiTagsInput.Clean')}}</el-button>
            </el-form-item>
        </el-form-item>
        <el-form-item :label="$t('Multi.User.billinggroup')" prop="billinggroup" v-if="usersForm.Filter=='billinggroup'">
            <el-select 
            v-model="usersForm.billinggroup" 
            :placeholder="$t(allable?'Multi.User.All':'Multi.User.PleaseSelect')" 
            multiple 
            :multiple-limit="maxValue.billinggroup">
                <el-option v-for="item in usersData.billinggroup" 
                :key="item.id" 
                :value="item.id" 
                :label="item.name"></el-option>
            </el-select>
            <el-form-item  v-show="usersForm.billinggroup.length>0">
                <el-button @click="onClearClick" type="danger" size="mini">{{$t('MultiTagsInput.Clean')}}</el-button>
            </el-form-item>
        </el-form-item>        
    </composite-form-dialog>
</template>

<script>
import CompositeFormDialog from '../../component/composite-form-dialog'
import UserGroupService from '../../service/user-group'
import BillGroupService from '../../service/bill-group'
import ValidRoleFactory from '../../common/valid-role-factory'

export default {
    data(){
        return {
            usersForm: {
                Filter: this.FilterKey,
                usergroup: [],
                billinggroup: [],
                username: ''
            },
            usersData: {
                usergroup: [],
                billinggroup: []
            },
            usersRules: {
                username: [
                    ValidRoleFactory.getValidUsersName(this.allable,this.maxValue.username)
                ],
                usergroup: [
                    ValidRoleFactory.getValidMultiSelect(this.allable)
                ],
                billinggroup: [
                    ValidRoleFactory.getValidMultiSelect(this.allable)
                ]
            }
        }
    },
    props: [
        'formValue',
        'filterList',
        'allable',
        'maxValue'
    ],
    components: {
        'composite-form-dialog': CompositeFormDialog
    },
    methods:{
        init(){
            this.usersForm = {
                Filter: this.formValue.value_type,
                usergroup: this.formValue.value_type=='usergroup'?this.formValue.values:[],
                billinggroup: this.formValue.value_type=='billinggroup'?this.formValue.values:[],
                username: this.formValue.value_type=='username'?this.formValue.values.join(','):[]
            };
            this.getGroups();
            this.$refs.innerDialog.emptyPopup().then(()=>{
                var data = this.doConfirm();
                this.$emit('on-selected',data);
            }).catch((err)=>{
                //do Nothing
            });
        },
        clearState(){
            this.usersForm = {
                Filter: this.usersForm.Filter,
                usergroup: [],
                billinggroup: [],
                username: ''
            };
            this.$refs.innerDialog.$refs.innerForm.clearValidate();
        },
        getGroups(){
            UserGroupService.getAllUserGroups().then((res)=>{
                this.usersData.usergroup = res.sort((a,b)=>a.name.localeCompare(b.name));
            });
            BillGroupService.getAllBillGroups().then((res)=>{
                this.usersData.billinggroup = res.sort((a,b)=>a.name.localeCompare(b.name));
            });
        },
        doConfirm(){
            var newData = {
                values: [],
                value_type: this.usersForm.Filter
            }
            var values = [];
            if(this.usersForm.Filter=='username'){
                values = this.usersForm.username==''?[]:this.usersForm.username.split(',');
            }else{
                values = this.usersForm[this.usersForm.Filter];
            }
            newData.values = values;

            return newData
        },
        onClearClick(){
            this.usersForm.usergroup = [];
            this.usersForm.billinggroup = [];
            this.usersForm.username = '';
        }
    }
}
</script>
