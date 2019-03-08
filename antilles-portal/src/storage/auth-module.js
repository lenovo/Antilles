/*
 * Copyright © 2019-present Lenovo
 * 
 * This file is licensed under both the BSD-3 license for individual/non-commercial use and
 * EPL-1.0 license for commercial use. Full text of both licenses can be found in
 * COPYING.BSD and COPYING.EPL files.
 */

// Define auth storage module
import Session from '../common/session'
import Parser from '../common/parser'

// Define state
const state = {
	username: '',
	userid: '',
	role: '',
	access: '',
	token: '',
	// ldap: '',
	ldapManaged: true,
	// ldapDefaultUsername: '',
	featureCodes: []
}

// Define mutations
const mutations = {
	setUser(state, payload) {
		state.username = payload.username;
		state.userid = payload.userid;
		state.role = payload.role;
		state.access = payload.access;
		state.token = payload.token;
		// state.ldap = payload.ldap;
		state.ldapManaged = payload.ldapManaged;
		// state.ldapDefaultUsername = payload.ldapDefaultUsername;
		state.featureCodes = payload.featureCodes;
		Session.setValue('antilles_username', payload.username);
		Session.setValue('antilles_userid', payload.userid);
		Session.setValue('antilles_role', payload.role);
		Session.setValue('antilles_access', payload.access);
		Session.setValue('antilles_token', payload.token);
		// Session.setValue('antilles_ldap', payload.ldap);
		Session.setValue('antilles_ldap_managed', payload.ldapManaged);
		// Session.setValue('antilles_ldap_default_username', payload.ldapDefaultUsername);
		if(payload.featureCodes) {
			Session.setValue('antilles_feature_codes', payload.featureCodes.join(','));
		} else {
			Session.setValue('antilles_feature_codes', '');
		}
	}
}

// Define actions
const actions = {
	init(context) {
		context.commit('setUser', {
			username: Session.getValue('antilles_username', ''),
			userid: Session.getValue('antilles_userid', ''),
			role: Session.getValue('antilles_role', ''),
			access: Session.getValue('antilles_access', ''),
			token: Session.getValue('antilles_token', ''),
			// ldap: Session.getValue('antilles_ldap', ''),
			ldapManaged: Parser.parseBooleanFromString(Session.getValue('antilles_ldap_managed', 'true')),
			// ldapDefaultUsername: Session.getValue('antilles_ldap_default_username', ''),
			featureCodes: Session.getValue('antilles_feature_codes', '').split(',')
		});
	},
  login(context, payload) {
		context.commit('setUser', payload);
  },
	setAccess(context, access) {
		context.commit('setUser', {
			username: Session.getValue('antilles_username', ''),
			userid: Session.getValue('antilles_userid', ''),
			role: Session.getValue('antilles_role', ''),
			access: access,
			token: Session.getValue('antilles_token', ''),
			// ldap: Session.getValue('antilles_ldap', ''),
			ldapManaged: Parser.parseBooleanFromString(Session.getValue('antilles_ldap_managed', 'true')),
			// ldapDefaultUsername: Session.getValue('antilles_ldap_default_username', ''),
			featureCodes: Session.getValue('antilles_feature_codes', '').split(',')
		});
	},
	setLDAP(context, ldap) {
		context.commit('setUser', {
			username: Session.getValue('antilles_username', ''),
			userid: Session.getValue('antilles_userid', ''),
			role: Session.getValue('antilles_role', ''),
			access: Session.getValue('antilles_access', ''),
			token: Session.getValue('antilles_token', ''),
			// ldap: ldap,
			ldapManaged: Parser.parseBooleanFromString(Session.getValue('antilles_ldap_managed', 'true')),
			// ldapDefaultUsername: Session.getValue('antilles_ldap_default_username', ''),
			featureCodes: Session.getValue('antilles_feature_codes', '').split(',')
		});
	},
	setLDAPManaged(context, payload) {
		context.commit('setUser', {
			username: Session.getValue('antilles_username', ''),
			userid: Session.getValue('antilles_userid', ''),
			role: Session.getValue('antilles_role', ''),
			access: Session.getValue('antilles_access', ''),
			token: Session.getValue('antilles_token', ''),
			// ldap: Session.getValue('antilles_ldap', ''),
			ldapManaged: payload.ldapManaged,
			// ldapDefaultUsername: payload.ldapDefaultUsername,
			featureCodes: Session.getValue('antilles_feature_codes', '').split(',')
		});
	},
	setToken(context, payload) {
		context.commit('setUser', {
			username: payload.username,
			userid: payload.userid,
			role: payload.role,
			access: Session.getValue('antilles_access', ''),
			token: payload.token,
			// ldap: Session.getValue('antilles_ldap', ''),
			ldapManaged: Parser.parseBooleanFromString(Session.getValue('antilles_ldap_managed', 'true')),
			// ldapDefaultUsername: Session.getValue('antilles_ldap_default_username', ''),
			featureCodes: Session.getValue('antilles_feature_codes', '').split(',')
		});
	},
	setFeatureCodes(context, payload) {
		context.commit('setUser', {
			username: Session.getValue('antilles_username', ''),
			userid: Session.getValue('antilles_userid', ''),
			role: Session.getValue('antilles_role', ''),
			access: Session.getValue('antilles_access', ''),
			token: Session.getValue('antilles_token', ''),
			// ldap: Session.getValue('antilles_ldap', ''),
			ldapManaged: Parser.parseBooleanFromString(Session.getValue('antilles_ldap_managed', 'true')),
			// ldapDefaultUsername: Session.getValue('antilles_ldap_default_username', ''),
			featureCodes: payload.featureCodes
		});
	},
	logout(context) {
		context.commit('setUser', {
			username: '',
			userid: '',
			role: '',
			access: '',
			token: '',
			// ldap: '',
			ldapManaged: true,
			// ldapDefaultUsername: '',
			featureCodes: []
		});
		Session.clear();
	}
}

// Define module
const authModule = {
	namespaced: true,
  state: state,
  mutations: mutations,
  actions: actions
}

export default authModule
