<style lang="">
	.login{
		position:relative;
    background: #333c4b;
    background-image:url("../asset/image/back.png");
		background-size: cover;
    min-height: 100%;
	}
	.login-logo{
		position: absolute;
    top: 50px;
    left: 50px;
	}
	.login-container{
    position: absolute;
    transform: translate(-50%,-50%);
    top:50%;
    left:50%;
    min-width:300px;
    max-width: 400px;
    padding: 30px 30px 20px;
    background: #fff;
    border-radius: 4px;
    box-shadow: 0 2px 16px #333c4b, 0 0 1px #333c4b, 0 0 1px #333c4b;
  }
  .login-h2{
    font-size:24px;
    font-weight: normal;
  }
  .login-footer{
    position: fixed;
    bottom: 0;
    left:0;
    margin:20px auto;
    font-size: 12px;
    color: #eee;
    width: 100%;
    text-align: center;
  }

  .select-language{width: 100%;height: 0;}
  .select-language>.el-dropdown{float: right;margin: 45px 50px 0 0;}
  .select-language>.el-dropdown>p{padding: 0 10px 0 10px;border: 1px solid white;border-radius: 4px;width: 70px;cursor: pointer;}
  .select-language>.el-dropdown>p>span{display: inline-block;line-height: 40px;font-size: 14px;color: white;width: 50px;}
  .select-language>.el-dropdown>p>i{color: white;}

  .lang-menu{background-color: rgba(0,0,0,.1);border: none;padding: 4px 0;width: 92px;}
  .lang-menu>.el-dropdown-menu__item{color: white;padding-left: 10px;}
  .lang-menu>.el-dropdown-menu__item:hover{background-color: rgba(0,0,0,.2);color: white;}
  .el-popper>.popper__arrow::after {
    content: " ";
    border-width: 0px;
  }
  .el-popper[x-placement^=bottom] .popper__arrow {
    border-bottom-color: rgba(0,0,0,0);
  }
</style>
<template>
	<div class="login" >
		<div class="login-logo">
		  <img src="../asset/image/login-logo.png">
		</div>
    <div class="select-language">
      <el-dropdown trigger="hover" @command="setLangCode">
        <p class="el-dropdown-link">
          <span>{{getLangType}}</span><i class="el-icon-arrow-down el-icon--right"></i>
        </p>
        <el-dropdown-menu class="lang-menu" slot="dropdown">
          <el-dropdown-item v-for="langType of langTypes"
                            :command="langType.code"
                            :key="langType.code">
            {{langType.type}}
          </el-dropdown-item>
        </el-dropdown-menu>
      </el-dropdown>
    </div>
		<div class="login-container"@keyup.enter="login('loginForm')" >
			<div class="login-content">
        <el-form :model="loginForm" :rules="loginRules" ref="loginForm" >
          <el-form-item style="text-align: center">
            <h2 class="login-h2">{{$t("Login.Title")}}</h2>
          </el-form-item>
          <el-form-item prop="username" style="text-align: center">
            <el-input id="tid_login-username" type="text" v-model="loginForm.username" auto-complete="off" :placeholder="$t('Login.Username.Placeholder')" :disabled="loading" :autofocus='true'></el-input>
          </el-form-item>
          <el-form-item prop="password" style="text-align: center">
            <el-input id="tid_login-password" type="password" v-model="loginForm.password" auto-complete="off" :placeholder="$t('Login.Password.Placeholder')" :disabled="loading"></el-input>
          </el-form-item>
          <el-form-item style="text-align: center;">
            <el-button id="tid_login-submit" style="width: 150px; margin-top: 10px;" type="primary" :loading="loading" @click="login('loginForm')">{{$t("Login.Submit")}}</el-button>
          </el-form-item>
        </el-form>
      </div>
		</div>
    <div class="login-footer">
      <span>{{$t("Version")}}</span>{{version}} &nbsp;
      <span>{{$t("Copyright")}}</span>&nbsp;&nbsp;
      <a href="/config/notice" target="_blank" style="color:white;text-decoration: underline;">{{$t("Login.About")}}</a>
    </div>
	</div>
</template>
<script>
	import AuthService from "../service/auth"
  import locale from 'element-ui/lib/locale'
  import elemantLang from '../locale/element-ui-messages'

	 export default {
    data() {
			var validateUsername = (rule, value, callback) => {
        if (!value) {
          return callback(new Error(this.$t("Login.Username.Valid.Null")));
        }else{
          callback();
        }
      };
      var validatePassword = (rule, value, callback) => {
        if (value === '') {
          callback(new Error(this.$t("Login.Password.Valid.Null")));
        }else{
          callback();
        }
      };
      return {
        loginForm: {
          password: '',
          username: ''
        },
        loginRules: {
          password: [
            { validator: validatePassword, trigger: 'blur' }
          ],
          username: [
            { validator: validateUsername, trigger: 'blur' }
          ]
        },
				loading: false,
				version: '',
        langTypes:[
          {type:'English',code:'en'},
          {type:'中文',code:'zh'}
        ]
      };
    },
     created(){
       // Setting language
       let getLangCode = this.$store.state.settings.langCode;
       this.$i18n.locale=getLangCode;
       locale.use(elemantLang[getLangCode]);
     },
		mounted() {
			console.log("Login mounted");
			this.checkVersion();
			this.checkLogin();
		},
     computed:{
       getLangType(){
         for (let i in this.langTypes){
           if (this.$store.state.settings.langCode==this.langTypes[i].code){
             return this.langTypes[i].type
           }
         }
       }
     },
    methods: {
      setLangCode(langCodeType){
        this.$store.dispatch('settings/setLangCode',langCodeType);
        window.location.reload();
      },
			checkVersion() {
				AuthService.getVersion().then((res) => {
					this.version = res;
				}, (res) => {
					this.$message.error(res);
				});
			},
      login(formName) {
        this.$refs[formName].validate((valid) => {
          if (valid) {
						this.loading = true;
            AuthService.login(this.loginForm.username,this.loginForm.password).then(() => {
							this.checkConfig();
            }, (errMsg) => {
							this.loading = false;
              this.$message.error(errMsg);
            });
          } else {
            return false;
          }
        });
      },
			checkConfig() {
				AuthService.checkConfig().then(() => {
					this.loading = false;
					let self = this;
					window.startAsync(window.asyncCallback.bind({username: 'demouser'}));
					this.$router.push({ path: '/main' });
				}, (errMsg) => {
					this.loading = false;
					this.$message.error(errMsg);
				});
			},
			checkLogin() {
				if(AuthService.isLogin()) {
					this.$router.push({ path: '/main' });
				}
			}
    }
  }
</script>
