from jsonrpc2_base.client import Client
from metal_cloud_sdk.objects.utils.deserializer import Deserializer
from metal_cloud_sdk.objects.utils.serializer import Serializer
from jsonrpc2_base.jsonrpc_exception import JSONRPCException

class IPCBilling2(Client):
	__instance = None

	def __init__(self, dictParams, arrFilterPlugins = []):
		super(IPCBilling2, self).__init__(dictParams, arrFilterPlugins)

	@staticmethod
	def getInstance(dictParams, arrFilterPlugins = []):
		"""
		This is a static function for using the IPCBilling2 class as a singleton.
		In order to work with only an instance, instead of instantiating the class,
		call this method.

		@return object IPCBilling2.__instance. It will return the same instance, no matter
		how many times this function is called.
		"""
		if IPCBilling2.__instance is None :
			IPCBilling2.__instance = IPCBilling2(dictParams, arrFilterPlugins)

		return IPCBilling2.__instance


	""" 27 functions available on endpoint. """

	def resource_utilization_summary(self, strUserIDOwner, strStartTimestamp, strEndTimestamp, arrInfrastructureIDs = Non):

		arrParams = [
			strUserIDOwner,
			strStartTimestamp,
			strEndTimestamp,
			arrInfrastructureIDs,
		]

		return self.rpc("resource_utilization_summary", arrParams)


	def resource_utilization_summary_start_timestamp_default(self, strUserI):

		arrParams = [
			strUserID,
		]

		return self.rpc("resource_utilization_summary_start_timestamp_default", arrParams)


	def user_sync_from_billing2(self, objUserData_Billing2, strPassword = None, strAuthenticatorSharedSecretBase32 = None, objLoginEvent = Non):

		objUserData_Billing2 = Serializer.serialize(objUserData_Billing2)
		objLoginEvent = Serializer.serialize(objLoginEvent)

		arrParams = [
			objUserData_Billing2,
			strPassword,
			strAuthenticatorSharedSecretBase32,
			objLoginEvent,
		]

		return self.rpc("user_sync_from_billing2", arrParams)


	def user_ids_to_emails(self):

		arrParams = [
		]

		return self.rpc("user_ids_to_emails", arrParams)


	def user_get(self, strUserI):

		arrParams = [
			strUserID,
		]

		return Deserializer.deserialize(self.rpc("user_get", arrParams))

	def user_jwt_check(self, strEncodedCookie, nUserIdBS):

		arrParams = [
			strEncodedCookie,
			nUserIdBSI,
		]

		return self.rpc("user_jwt_check", arrParams)


	def user_suspend_reason_add(self, nUserID, strSuspendReasonType, strSuspendReasonPublicComment, strSuspendReasonPrivateComment = "):

		arrParams = [
			nUserID,
			strSuspendReasonType,
			strSuspendReasonPublicComment,
			strSuspendReasonPrivateComment,
		]

		return Deserializer.deserialize(self.rpc("user_suspend_reason_add", arrParams))

	def user_suspend_reason_remove(self, nUserID, strSuspendReasonTyp):

		arrParams = [
			nUserID,
			strSuspendReasonType,
		]

		self.rpc("user_suspend_reason_remove", arrParams)


	def jwt_session_cookies_types_to_cookies_names(self):

		arrParams = [
		]

		return self.rpc("jwt_session_cookies_types_to_cookies_names", arrParams)


	def infrastructures(self, strUserID, arrInfrastructureIDs = Non):

		arrParams = [
			strUserID,
			arrInfrastructureIDs,
		]

		objInfrastructure = self.rpc("infrastructures", arrParams)
		for strKeyInfrastructure in objInfrastructure:
			objInfrastructure[strKeyInfrastructure] = Deserializer.deserialize(objInfrastructure[strKeyInfrastructure])
		return objInfrastructure

	def user_billable_set(self, nUserID, bBillabl):

		arrParams = [
			nUserID,
			bBillable,
		]

		return self.rpc("user_billable_set", arrParams)


	def datacenters(self, strUserID = None, bOnlyActive = False, bIncludeConfigProperties = Fals):

		arrParams = [
			strUserID,
			bOnlyActive,
			bIncludeConfigProperties,
		]

		objDatacenter = self.rpc("datacenters", arrParams)
		for strKeyDatacenter in objDatacenter:
			objDatacenter[strKeyDatacenter] = Deserializer.deserialize(objDatacenter[strKeyDatacenter])
		return objDatacenter

	def volume_template_get(self, strVolumeTemplateI):

		arrParams = [
			strVolumeTemplateID,
		]

		return Deserializer.deserialize(self.rpc("volume_template_get", arrParams))

	def volume_templates_public(self, arrVolumeTemplateIDs = Non):

		arrParams = [
			arrVolumeTemplateIDs,
		]

		objVolumeTemplate = self.rpc("volume_templates_public", arrParams)
		for strKeyVolumeTemplate in objVolumeTemplate:
			objVolumeTemplate[strKeyVolumeTemplate] = Deserializer.deserialize(objVolumeTemplate[strKeyVolumeTemplate])
		return objVolumeTemplate

	def volume_templates_private(self, strUserID, arrVolumeTemplateIDs = Non):

		arrParams = [
			strUserID,
			arrVolumeTemplateIDs,
		]

		objVolumeTemplate = self.rpc("volume_templates_private", arrParams)
		for strKeyVolumeTemplate in objVolumeTemplate:
			objVolumeTemplate[strKeyVolumeTemplate] = Deserializer.deserialize(objVolumeTemplate[strKeyVolumeTemplate])
		return objVolumeTemplate

	def volume_templates(self, strUserID, arrVolumeTemplateIDs = Non):

		arrParams = [
			strUserID,
			arrVolumeTemplateIDs,
		]

		objVolumeTemplate = self.rpc("volume_templates", arrParams)
		for strKeyVolumeTemplate in objVolumeTemplate:
			objVolumeTemplate[strKeyVolumeTemplate] = Deserializer.deserialize(objVolumeTemplate[strKeyVolumeTemplate])
		return objVolumeTemplate

	def server_type_get(self, strServerTypeI):

		arrParams = [
			strServerTypeID,
		]

		return Deserializer.deserialize(self.rpc("server_type_get", arrParams))

	def server_types(self, strDatacenterName = None, bOnlyAvailable = Fals):

		arrParams = [
			strDatacenterName,
			bOnlyAvailable,
		]

		objServerType = self.rpc("server_types", arrParams)
		for strKeyServerType in objServerType:
			objServerType[strKeyServerType] = Deserializer.deserialize(objServerType[strKeyServerType])
		return objServerType

	def server_type_matches(self, strInfrastructureID, objHardwareConfiguration, strInstanceArrayID = None, bAllowServerSwap = Fals):

		objHardwareConfiguration = Serializer.serialize(objHardwareConfiguration)

		arrParams = [
			strInfrastructureID,
			objHardwareConfiguration,
			strInstanceArrayID,
			bAllowServerSwap,
		]

		return self.rpc("server_type_matches", arrParams)


	def server_types_datacenter(self, strDatacenterNam):

		arrParams = [
			strDatacenterName,
		]

		return self.rpc("server_types_datacenter", arrParams)


	def server_types_match_hardware_configuration(self, strDatacenterName, objHardwareConfiguratio):

		objHardwareConfiguration = Serializer.serialize(objHardwareConfiguration)

		arrParams = [
			strDatacenterName,
			objHardwareConfiguration,
		]

		objServerType = self.rpc("server_types_match_hardware_configuration", arrParams)
		for strKeyServerType in objServerType:
			objServerType[strKeyServerType] = Deserializer.deserialize(objServerType[strKeyServerType])
		return objServerType

	def user_plan_type_get(self, nUserI):

		arrParams = [
			nUserID,
		]

		return self.rpc("user_plan_type_get", arrParams)


	def user_plan_type_set(self, nUserID, strUserPlanType, objPlanTemplate = Non):

		objPlanTemplate = Serializer.serialize(objPlanTemplate)

		arrParams = [
			nUserID,
			strUserPlanType,
			objPlanTemplate,
		]

		return self.rpc("user_plan_type_set", arrParams)


	def user_delete_from_billing2(self, nUserID, bTargetOnlyTestUsers = Tru):

		arrParams = [
			nUserID,
			bTargetOnlyTestUsers,
		]

		self.rpc("user_delete_from_billing2", arrParams)


	def user_password_change_from_billing2(self, nUserID, strNewPassword, bMustChangePasswordAtNextLogin = Fals):

		arrParams = [
			nUserID,
			strNewPassword,
			bMustChangePasswordAtNextLogin,
		]

		return self.rpc("user_password_change_from_billing2", arrParams)


	def identity_user_create_from_billing2(self, objUserData, bMustChangePasswordAtNextLogin = True, strPassword = Non):

		objUserData = Serializer.serialize(objUserData)

		arrParams = [
			objUserData,
			bMustChangePasswordAtNextLogin,
			strPassword,
		]

		return self.rpc("identity_user_create_from_billing2", arrParams)


	def identity_user_auth_from_billing2(self, strEmail, strPassword, strOneTimePassword = Non):

		arrParams = [
			strEmail,
			strPassword,
			strOneTimePassword,
		]

		return self.rpc("identity_user_auth_from_billing2", arrParams)


