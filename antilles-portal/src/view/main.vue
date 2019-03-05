<style>

	/*@media (min-width:1000px) and (min-height: 750px) {
		.main-wrapper {
			height: 100%
		}
	}*/

	.main-wrapper {
		min-height: 100%;
		position: relative;
		/*overflow: hidden;*/
	}
	.main-sidebar {
		position: absolute;
		top: 0;
		left: 0;
		min-height: 100%;
		width: 236px;
		display: block;
		background-color: #343C4A;
		transition: transform .3s ease-in-out,width .3s ease-in-out;
	}
	.main-sidebar-min {
		width: 64px;
	}
	.main-content-wrapper {
		height: 100%;
		margin-left: 236px;
		display: flex;
		flex-direction: column;
		transition: transform .3s ease-in-out,margin .3s ease-in-out;
	}
	.main-content-wrapper-max {
		margin-left: 64px;
	}
	.main-contents {
		height: 100%;
		box-sizing: border-box;
		padding: 10px;
		display: flex;
		flex-direction: column;
	}

</style>
<template>
	<div class="main-wrapper">
		<div class="main-sidebar" :class="isMin ? 'main-sidebar-min' : ''">
			<leftbar id="tid_main-left-bar"></leftbar>
		</div>
		<div class="main-content-wrapper" :class="isMin ? 'main-content-wrapper-max' : ''">
			<el-row>
				<topbar id="tid_main-top-bar"></topbar>
			</el-row>
			<div id="tid_main-content" class="main-contents">
				<breadcrumb-bar></breadcrumb-bar>
				<router-view></router-view>
			</div>
		</div>
	</div>
<!--
	<el-row id="main" class="main">
		<div class="main-left" :class="isMin?'main-left-min':'main-left-max'">
			<leftbar></leftbar>
		</div>
		<div class="main-right" :class="isMin?'main-right-max':'main-left-min'">
			<el-row>
				<topbar></topbar>
			</el-row>
			<el-row class="main-contents">
				<router-view></router-view>
			</el-row>
		</div>
	</el-row> -->
</template>
<script>
	import leftbar from './main/leftbar'
	import topbar from './main/topbar'
	import BreadcrumbBar from '../widget/breadcrumb-bar'
	import AccessService from '../service/access'
  import locale from 'element-ui/lib/locale'
  import elemantLang from '../locale/element-ui-messages'

	export default {
		data () {
			return {
				isMin: gApp.isCollapse
			}
		},
		mounted() {
      console.log("Main mounted");
			this.selectDefaultMenu();
			var _this = this
      gApp.$watch('isCollapse',function (newValue, oldValue) {
				_this.isMin = newValue
      })
    },
		created(){
      // Setting language
      let getLangCode = this.$store.state.settings.langCode;
      this.$i18n.locale=getLangCode;
      locale.use(elemantLang[getLangCode]);
		},
		components: {
			'leftbar': leftbar ,
			'topbar': topbar,
			'breadcrumb-bar': BreadcrumbBar
		},
		methods: {
			selectDefaultMenu() {
				if(this.$route.path == '/main'){
					var menuList = AccessService.getMenuByAccess(this.$store.state.auth.access);
					if(menuList.length > 0) {
						this.$router.push({ path: menuList[0].path });
					}
				}
			}
		}
	}
</script>
