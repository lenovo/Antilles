/*
 * Copyright © 2019-present Lenovo
 * 
 * This file is licensed under both the BSD-3 license for individual/non-commercial use and
 * EPL-1.0 license for commercial use. Full text of both licenses can be found in
 * COPYING.BSD and COPYING.EPL files.
 */

import 'babel-polyfill'
// Import Vue.js
import Vue from 'vue'
// Import Vue.js core libraries
import VueResource from 'vue-resource'
import VueRouter from 'vue-router'
import VueI18n from 'vue-i18n'
// Import element-ui library
import ElementUI from 'element-ui'
import locale from 'element-ui/lib/locale'
// Import theme for element-ui, need to replace with customized theme
import 'element-ui/lib/theme-chalk/index.css'
import './asset/theme/antilles/index.css'
// Import Antilles main css
import './asset/css/main.css'
// Import iconfont
import './asset/theme/antilles/fonts/iconfont.css'

// Import Antilles things
import Utils from './common/utils'
import store from './storage/store'
import routes from './router/route'
import messages from './locale/messages'
import elemantLang from './locale/element-ui-messages'

import AuthService from './service/auth'
import AccessService from './service/access'
import App from './app'

// Install libraries into Vue.js
Vue.use(VueResource);
Vue.use(VueRouter);
Vue.use(VueI18n);

/*	Elemant Select 组件的 popperAppendToBody 默认为 true
 *	会将 select option dialog 添加进 <body>标签
 *	autoTest case 无法进行定位元素
 */
//ElementUI.Select.props.popperAppendToBody.default = false;

Vue.use(ElementUI);


// Init VUE Route
const router = new VueRouter({
	mode: 'hash',
	routes
});

// Handle before route, need check auth information.
router.beforeEach((to, from, next) => {
	if (to.meta.auth && !AuthService.isLogin()) {
 		next({
 			path: '/login',
    	query: {redirect: to.fullPath}
    });
		return;
	}
	// if (to.meta.ldap && AuthService.isLDAPManaged()) {
	// 	if(!AuthService.isLDAPLogin()) {
	// 		next({
	// 			path: '/main/login-ldap',
	// 			query: {redirect: to.fullPath}
	// 		});
	// 		return;
	// 	}
	// }
	next();
});

// Handle after route
router.afterEach((to, from) => {
	// Nothing to do
});

// Init storage
store.dispatch('auth/init');

// Init locale
const browserLang = (navigator.language || navigator.browserLanguage).toLowerCase();
var langCode = 'en';
if(browserLang.indexOf('zh') >= 0) {
	langCode = 'zh';
}
const i18n = new VueI18n({
  locale: langCode,
  messages
});
locale.use(elemantLang[langCode]);

// Init auth for rest api
Vue.http.interceptors.push(function(request, next) {
	// Add token headers
	var token = window.gApp.$store.state.auth.token;
	if (token && token.length > 0) {
		request.headers.set('authorization', 'Jwt ' + token);
	}
	// Add LDAP headers
	// var ldap = window.gApp.$store.state.auth.ldap;
	// if(ldap && ldap.length > 0) {
	// 	request.headers.set('X-Antilles-User-Backend-Auth', ldap);
	// }
	next();
});

// New global Vue object
window.gApp = new Vue({
	el: '#app',
  i18n,
	store,
 	router,
	data: {
		isCollapse: false
	},
 	render: h => h(App)
});

// Start async service for Confluent termwindow
window.asyncCallback = function() {
	window.async_flag = true;
};
if(AuthService.isLogin()) {
	window.startAsync(window.asyncCallback.bind({username: 'demouser'}));
}


// Refresh Token Daemon
function refreshToken() {
	var token = window.gApp.$store.state.auth.token;
	if (token && token.length > 0) {
		AuthService.refreshToken().then((res) => {
			setTimeout(refreshToken, 1000 * 60 * 10);
		},
		(res) => {
			console.log("Refresh token failed.", res);
			AuthService.logout();
		});
	} else {
		setTimeout(refreshToken, 1000 * 60 * 10);
	}
}
refreshToken();
