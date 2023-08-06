from jsonrpc2_base.client import Client
from metal_cloud_sdk.objects.utils.deserializer import Deserializer
from metal_cloud_sdk.objects.utils.serializer import Serializer
from jsonrpc2_base.jsonrpc_exception import JSONRPCException

class API(Client):
	__instance = None

	def __init__(self, dictParams, arrFilterPlugins = []):
		super(API, self).__init__(dictParams, arrFilterPlugins)

	@staticmethod
	def getInstance(dictParams, arrFilterPlugins = []):
		"""
		This is a static function for using the API class as a singleton.
		In order to work with only an instance, instead of instantiating the class,
		call this method.

		@return object API.__instance. It will return the same instance, no matter
		how many times this function is called.
		"""
		if API.__instance is None :
			API.__instance = API(dictParams, arrFilterPlugins)

		return API.__instance


	""" 310 functions available on endpoint. """

	def cluster_create(self, strInfrastructureID, objCluste):

		objCluster = Serializer.serialize(objCluster)

		arrParams = [
			strInfrastructureID,
			objCluster,
		]

		return Deserializer.deserialize(self.rpc("cluster_create", arrParams))

	def cluster_get(self, strClusterID, bAccessSaaSAPI = True, nAccessSaaSAPITimeoutSeconds = 1):

		arrParams = [
			strClusterID,
			bAccessSaaSAPI,
			nAccessSaaSAPITimeoutSeconds,
		]

		return Deserializer.deserialize(self.rpc("cluster_get", arrParams))

	def cluster_edit(self, strClusterID, objClusterOperatio):

		objClusterOperation = Serializer.serialize(objClusterOperation)

		arrParams = [
			strClusterID,
			objClusterOperation,
		]

		return Deserializer.deserialize(self.rpc("cluster_edit", arrParams))

	def cluster_stop(self, strClusterI):

		arrParams = [
			strClusterID,
		]

		return Deserializer.deserialize(self.rpc("cluster_stop", arrParams))

	def cluster_start(self, strClusterI):

		arrParams = [
			strClusterID,
		]

		return Deserializer.deserialize(self.rpc("cluster_start", arrParams))

	def cluster_delete(self, strClusterI):

		arrParams = [
			strClusterID,
		]

		return Deserializer.deserialize(self.rpc("cluster_delete", arrParams))

	def clusters(self, strInfrastructureID, arrClusterIDs = None, bAccessSaaSAPI = False, nAccessSaaSAPITimeoutSeconds = 1):

		arrParams = [
			strInfrastructureID,
			arrClusterIDs,
			bAccessSaaSAPI,
			nAccessSaaSAPITimeoutSeconds,
		]

		objCluster = self.rpc("clusters", arrParams)
		for strKeyCluster in objCluster:
			objCluster[strKeyCluster] = Deserializer.deserialize(objCluster[strKeyCluster])
		return objCluster

	def cluster_suspend(self, strClusterI):

		arrParams = [
			strClusterID,
		]

		return Deserializer.deserialize(self.rpc("cluster_suspend", arrParams))

	def cluster_password_change(self, strClusterID, strNewPasswor):

		arrParams = [
			strClusterID,
			strNewPassword,
		]

		self.rpc("cluster_password_change", arrParams)


	def cluster_public_key_get(self, strClusterI):

		arrParams = [
			strClusterID,
		]

		return self.rpc("cluster_public_key_get", arrParams)


	def cluster_automatic_management_status_set(self, strClusterID, bStatu):

		arrParams = [
			strClusterID,
			bStatus,
		]

		self.rpc("cluster_automatic_management_status_set", arrParams)


	def container_array_create(self, strInfrastructureID, objContainerArra):

		objContainerArray = Serializer.serialize(objContainerArray)

		arrParams = [
			strInfrastructureID,
			objContainerArray,
		]

		return Deserializer.deserialize(self.rpc("container_array_create", arrParams))

	def container_array_get(self, strContainerArrayI):

		arrParams = [
			strContainerArrayID,
		]

		return Deserializer.deserialize(self.rpc("container_array_get", arrParams))

	def container_array_edit(self, strContainerArrayID, objContainerArrayOperation, bKeepDetachingDrives = Non):

		objContainerArrayOperation = Serializer.serialize(objContainerArrayOperation)

		arrParams = [
			strContainerArrayID,
			objContainerArrayOperation,
			bKeepDetachingDrives,
		]

		return Deserializer.deserialize(self.rpc("container_array_edit", arrParams))

	def container_array_delete(self, strContainerArrayI):

		arrParams = [
			strContainerArrayID,
		]

		return Deserializer.deserialize(self.rpc("container_array_delete", arrParams))

	def container_array_stop(self, strContainerArrayI):

		arrParams = [
			strContainerArrayID,
		]

		return Deserializer.deserialize(self.rpc("container_array_stop", arrParams))

	def container_array_start(self, strContainerArrayI):

		arrParams = [
			strContainerArrayID,
		]

		return Deserializer.deserialize(self.rpc("container_array_start", arrParams))

	def container_arrays(self, strInfrastructureID, arrContainerArrayIDs = Non):

		arrParams = [
			strInfrastructureID,
			arrContainerArrayIDs,
		]

		objContainerArray = self.rpc("container_arrays", arrParams)
		for strKeyContainerArray in objContainerArray:
			objContainerArray[strKeyContainerArray] = Deserializer.deserialize(objContainerArray[strKeyContainerArray])
		return objContainerArray

	def container_platform_container_arrays(self, strContainerPlatformID, arrContainerArrayIDs = Non):

		arrParams = [
			strContainerPlatformID,
			arrContainerArrayIDs,
		]

		objContainerArray = self.rpc("container_platform_container_arrays", arrParams)
		for strKeyContainerArray in objContainerArray:
			objContainerArray[strKeyContainerArray] = Deserializer.deserialize(objContainerArray[strKeyContainerArray])
		return objContainerArray

	def container_array_containers(self, strContainerArrayI):

		arrParams = [
			strContainerArrayID,
		]

		objContainer = self.rpc("container_array_containers", arrParams)
		for strKeyContainer in objContainer:
			objContainer[strKeyContainer] = Deserializer.deserialize(objContainer[strKeyContainer])
		return objContainer

	def container_cluster_create(self, strInfrastructureID, objContainerCluste):

		objContainerCluster = Serializer.serialize(objContainerCluster)

		arrParams = [
			strInfrastructureID,
			objContainerCluster,
		]

		return Deserializer.deserialize(self.rpc("container_cluster_create", arrParams))

	def container_cluster_get(self, strContainerClusterID, bAccessSaaSAPI = True, nAccessSaaSAPITimeoutSeconds = 1):

		arrParams = [
			strContainerClusterID,
			bAccessSaaSAPI,
			nAccessSaaSAPITimeoutSeconds,
		]

		return Deserializer.deserialize(self.rpc("container_cluster_get", arrParams))

	def container_cluster_edit(self, strContainerClusterID, objContainerClusterOperatio):

		objContainerClusterOperation = Serializer.serialize(objContainerClusterOperation)

		arrParams = [
			strContainerClusterID,
			objContainerClusterOperation,
		]

		return Deserializer.deserialize(self.rpc("container_cluster_edit", arrParams))

	def container_cluster_stop(self, strContainerClusterI):

		arrParams = [
			strContainerClusterID,
		]

		return Deserializer.deserialize(self.rpc("container_cluster_stop", arrParams))

	def container_cluster_start(self, strContainerClusterI):

		arrParams = [
			strContainerClusterID,
		]

		return Deserializer.deserialize(self.rpc("container_cluster_start", arrParams))

	def container_cluster_delete(self, strContainerClusterI):

		arrParams = [
			strContainerClusterID,
		]

		return Deserializer.deserialize(self.rpc("container_cluster_delete", arrParams))

	def container_clusters(self, strInfrastructureID, arrContainerClusterIDs = Non):

		arrParams = [
			strInfrastructureID,
			arrContainerClusterIDs,
		]

		objContainerCluster = self.rpc("container_clusters", arrParams)
		for strKeyContainerCluster in objContainerCluster:
			objContainerCluster[strKeyContainerCluster] = Deserializer.deserialize(objContainerCluster[strKeyContainerCluster])
		return objContainerCluster

	def container_cluster_suspend(self, strContainerClusterI):

		arrParams = [
			strContainerClusterID,
		]

		return Deserializer.deserialize(self.rpc("container_cluster_suspend", arrParams))

	def container_cluster_automatic_management_status_set(self, strContainerClusterID, bStatu):

		arrParams = [
			strContainerClusterID,
			bStatus,
		]

		self.rpc("container_cluster_automatic_management_status_set", arrParams)


	def container_platform_create(self, strInfrastructureID, objContainerPlatfor):

		objContainerPlatform = Serializer.serialize(objContainerPlatform)

		arrParams = [
			strInfrastructureID,
			objContainerPlatform,
		]

		return Deserializer.deserialize(self.rpc("container_platform_create", arrParams))

	def container_platform_get(self, strContainerPlatformI):

		arrParams = [
			strContainerPlatformID,
		]

		return Deserializer.deserialize(self.rpc("container_platform_get", arrParams))

	def container_platform_edit(self, strContainerPlatformID, objContainerPlatformOperation, objServerTypeMatches = Non):

		objContainerPlatformOperation = Serializer.serialize(objContainerPlatformOperation)
		objServerTypeMatches = Serializer.serialize(objServerTypeMatches)

		arrParams = [
			strContainerPlatformID,
			objContainerPlatformOperation,
			objServerTypeMatches,
		]

		return Deserializer.deserialize(self.rpc("container_platform_edit", arrParams))

	def container_platform_stop(self, strContainerPlatformI):

		arrParams = [
			strContainerPlatformID,
		]

		return Deserializer.deserialize(self.rpc("container_platform_stop", arrParams))

	def container_platform_start(self, strContainerPlatformI):

		arrParams = [
			strContainerPlatformID,
		]

		return Deserializer.deserialize(self.rpc("container_platform_start", arrParams))

	def container_platform_delete(self, strContainerPlatformI):

		arrParams = [
			strContainerPlatformID,
		]

		return Deserializer.deserialize(self.rpc("container_platform_delete", arrParams))

	def container_platforms(self, strInfrastructureID, arrContainerPlatformIDs = Non):

		arrParams = [
			strInfrastructureID,
			arrContainerPlatformIDs,
		]

		objContainerPlatform = self.rpc("container_platforms", arrParams)
		for strKeyContainerPlatform in objContainerPlatform:
			objContainerPlatform[strKeyContainerPlatform] = Deserializer.deserialize(objContainerPlatform[strKeyContainerPlatform])
		return objContainerPlatform

	def container_platform_suspend(self, strContainerPlatformI):

		arrParams = [
			strContainerPlatformID,
		]

		return Deserializer.deserialize(self.rpc("container_platform_suspend", arrParams))

	def data_lake_create(self, strInfrastructureID, objDataLak):

		objDataLake = Serializer.serialize(objDataLake)

		arrParams = [
			strInfrastructureID,
			objDataLake,
		]

		return Deserializer.deserialize(self.rpc("data_lake_create", arrParams))

	def data_lake_get(self, strDataLakeI):

		arrParams = [
			strDataLakeID,
		]

		return Deserializer.deserialize(self.rpc("data_lake_get", arrParams))

	def data_lake_edit(self, strDataLakeID, objDataLakeOperatio):

		objDataLakeOperation = Serializer.serialize(objDataLakeOperation)

		arrParams = [
			strDataLakeID,
			objDataLakeOperation,
		]

		return self.rpc("data_lake_edit", arrParams)


	def data_lake_stop(self, strDataLakeI):

		arrParams = [
			strDataLakeID,
		]

		return Deserializer.deserialize(self.rpc("data_lake_stop", arrParams))

	def data_lake_start(self, strDataLakeI):

		arrParams = [
			strDataLakeID,
		]

		return Deserializer.deserialize(self.rpc("data_lake_start", arrParams))

	def data_lake_delete(self, strDataLakeI):

		arrParams = [
			strDataLakeID,
		]

		return Deserializer.deserialize(self.rpc("data_lake_delete", arrParams))

	def data_lakes(self, strInfrastructureID, arrDataLakeIDs = Non):

		arrParams = [
			strInfrastructureID,
			arrDataLakeIDs,
		]

		objDataLake = self.rpc("data_lakes", arrParams)
		for strKeyDataLake in objDataLake:
			objDataLake[strKeyDataLake] = Deserializer.deserialize(objDataLake[strKeyDataLake])
		return objDataLake

	def data_lake_krb_conf_download_url(self):

		arrParams = [
		]

		return self.rpc("data_lake_krb_conf_download_url", arrParams)


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

	def fs_create(self, strFSURL, strType, strPermission = Non):

		arrParams = [
			strFSURL,
			strType,
			strPermission,
		]

		self.rpc("fs_create", arrParams)


	def fs_delete(self, strFSURL, bRecursive = Fals):

		arrParams = [
			strFSURL,
			bRecursive,
		]

		self.rpc("fs_delete", arrParams)


	def fs_download_url(self, strFSUR):

		arrParams = [
			strFSURL,
		]

		self.rpc("fs_download_url", arrParams)


	def fs_info(self, strFSUR):

		arrParams = [
			strFSURL,
		]

		self.rpc("fs_info", arrParams)


	def fs_list(self, strFSUR):

		arrParams = [
			strFSURL,
		]

		self.rpc("fs_list", arrParams)


	def fs_move(self, strFSURL, strPathNe):

		arrParams = [
			strFSURL,
			strPathNew,
		]

		self.rpc("fs_move", arrParams)


	def fs_owner_set(self, strFSURL, strOwne):

		arrParams = [
			strFSURL,
			strOwner,
		]

		self.rpc("fs_owner_set", arrParams)


	def fs_read(self, strFSURL, strEncoding, nOffset, nLengt):

		arrParams = [
			strFSURL,
			strEncoding,
			nOffset,
			nLength,
		]

		self.rpc("fs_read", arrParams)


	def fs_rename(self, strFSURL, strFilenameNe):

		arrParams = [
			strFSURL,
			strFilenameNew,
		]

		self.rpc("fs_rename", arrParams)


	def fs_truncate(self, strFSURL, nLengthNew = ):

		arrParams = [
			strFSURL,
			nLengthNew,
		]

		self.rpc("fs_truncate", arrParams)


	def fs_write(self, strFSURL, strContents, strEncoding, nOffset = None, bTruncate = Tru):

		arrParams = [
			strFSURL,
			strContents,
			strEncoding,
			nOffset,
			bTruncate,
		]

		self.rpc("fs_write", arrParams)


	def fs_upload_url(self, strFSUR):

		arrParams = [
			strFSURL,
		]

		return self.rpc("fs_upload_url", arrParams)


	def infrastructure_create(self, strUserID, objInfrastructure, strInfrastructureIDAsTemplate = Non):

		objInfrastructure = Serializer.serialize(objInfrastructure)

		arrParams = [
			strUserID,
			objInfrastructure,
			strInfrastructureIDAsTemplate,
		]

		return Deserializer.deserialize(self.rpc("infrastructure_create", arrParams))

	def infrastructure_deploy(self, strInfrastructureID, objShutdownOptions = None, objDeployOptions = None, bAllowDataLoss = False, bSkipAnsible = Fals):

		objShutdownOptions = Serializer.serialize(objShutdownOptions)
		objDeployOptions = Serializer.serialize(objDeployOptions)

		arrParams = [
			strInfrastructureID,
			objShutdownOptions,
			objDeployOptions,
			bAllowDataLoss,
			bSkipAnsible,
		]

		return Deserializer.deserialize(self.rpc("infrastructure_deploy", arrParams))

	def infrastructure_get(self, strInfrastructureI):

		arrParams = [
			strInfrastructureID,
		]

		return Deserializer.deserialize(self.rpc("infrastructure_get", arrParams))

	def infrastructure_operation_cancel(self, strInfrastructureI):

		arrParams = [
			strInfrastructureID,
		]

		self.rpc("infrastructure_operation_cancel", arrParams)


	def infrastructure_edit(self, strInfrastructureID, objInfrastructureOperatio):

		objInfrastructureOperation = Serializer.serialize(objInfrastructureOperation)

		arrParams = [
			strInfrastructureID,
			objInfrastructureOperation,
		]

		return Deserializer.deserialize(self.rpc("infrastructure_edit", arrParams))

	def infrastructure_deploy_options(self, strInfrastructureID, bReplaceServerTypes = Fals):

		arrParams = [
			strInfrastructureID,
			bReplaceServerTypes,
		]

		return self.rpc("infrastructure_deploy_options", arrParams)


	def infrastructure_deploy_overview(self, strInfrastructureID, objDeployOptions = Non):

		objDeployOptions = Serializer.serialize(objDeployOptions)

		arrParams = [
			strInfrastructureID,
			objDeployOptions,
		]

		return Deserializer.deserialize(self.rpc("infrastructure_deploy_overview", arrParams))

	def infrastructure_delete(self, strInfrastructureI):

		arrParams = [
			strInfrastructureID,
		]

		return Deserializer.deserialize(self.rpc("infrastructure_delete", arrParams))

	def infrastructure_user_limits(self, strInfrastructureI):

		arrParams = [
			strInfrastructureID,
		]

		return Deserializer.deserialize(self.rpc("infrastructure_user_limits", arrParams))

	def infrastructure_deploy_blockers(self, strInfrastructureI):

		arrParams = [
			strInfrastructureID,
		]

		arrInfrastructureDeployBlockers = self.rpc("infrastructure_deploy_blockers", arrParams)
		for index in range(len(arrInfrastructureDeployBlockers)):
			arrInfrastructureDeployBlockers[index] = Deserializer.deserialize(arrInfrastructureDeployBlockers[index])
		return arrInfrastructureDeployBlockers

	def infrastructure_design_lock_set(self, strInfrastructureID, bLockStatu):

		arrParams = [
			strInfrastructureID,
			bLockStatus,
		]

		self.rpc("infrastructure_design_lock_set", arrParams)


	def infrastructure_deploy_shutdown_required(self, strInfrastructureID, strPowerCommand = "none", bOnlyPoweredOn = Tru):

		arrParams = [
			strInfrastructureID,
			strPowerCommand,
			bOnlyPoweredOn,
		]

		return self.rpc("infrastructure_deploy_shutdown_required", arrParams)


	def infrastructures(self, strUserID, arrInfrastructureIDs = Non):

		arrParams = [
			strUserID,
			arrInfrastructureIDs,
		]

		objInfrastructure = self.rpc("infrastructures", arrParams)
		for strKeyInfrastructure in objInfrastructure:
			objInfrastructure[strKeyInfrastructure] = Deserializer.deserialize(objInfrastructure[strKeyInfrastructure])
		return objInfrastructure

	def infrastructure_user_add(self, strInfrastructureID, strUserEmail, objInfrastructurePermissions = None, bCreateUserIfNotExists = Fals):

		objInfrastructurePermissions = Serializer.serialize(objInfrastructurePermissions)

		arrParams = [
			strInfrastructureID,
			strUserEmail,
			objInfrastructurePermissions,
			bCreateUserIfNotExists,
		]

		self.rpc("infrastructure_user_add", arrParams)


	def infrastructure_user_remove(self, strInfrastructureID, strUserI):

		arrParams = [
			strInfrastructureID,
			strUserID,
		]

		return self.rpc("infrastructure_user_remove", arrParams)


	def infrastructure_user_update(self, strInfrastructureID, strUserEmail, objInfrastructurePermission):

		objInfrastructurePermissions = Serializer.serialize(objInfrastructurePermissions)

		arrParams = [
			strInfrastructureID,
			strUserEmail,
			objInfrastructurePermissions,
		]

		self.rpc("infrastructure_user_update", arrParams)


	def infrastructure_user_ssh_keys(self, strInfrastructureI):

		arrParams = [
			strInfrastructureID,
		]

		return self.rpc("infrastructure_user_ssh_keys", arrParams)


	def infrastructure_users(self, strInfrastructureID, arrUserIDs = Non):

		arrParams = [
			strInfrastructureID,
			arrUserIDs,
		]

		objUser = self.rpc("infrastructure_users", arrParams)
		for strKeyUser in objUser:
			objUser[strKeyUser] = Deserializer.deserialize(objUser[strKeyUser])
		return objUser

	def instance_server_power_set_batch(self, strInfrastructureID, arrInstanceIDs, strPowerComman):

		arrParams = [
			strInfrastructureID,
			arrInstanceIDs,
			strPowerCommand,
		]

		self.rpc("instance_server_power_set_batch", arrParams)


	def instance_server_power_get_batch(self, strInfrastructureID, arrInstanceID):

		arrParams = [
			strInfrastructureID,
			arrInstanceIDs,
		]

		return self.rpc("instance_server_power_get_batch", arrParams)


	def instance_edit(self, strInstanceID, objInstanceOperatio):

		objInstanceOperation = Serializer.serialize(objInstanceOperation)

		arrParams = [
			strInstanceID,
			objInstanceOperation,
		]

		return Deserializer.deserialize(self.rpc("instance_edit", arrParams))

	def instance_delete(self, strInstanceID, bKeepDetachingDrive):

		arrParams = [
			strInstanceID,
			bKeepDetachingDrives,
		]

		return Deserializer.deserialize(self.rpc("instance_delete", arrParams))

	def instance_server_power_get(self, strInstanceI):

		arrParams = [
			strInstanceID,
		]

		return self.rpc("instance_server_power_get", arrParams)


	def instance_server_power_set(self, strInstanceID, strPowerComman):

		arrParams = [
			strInstanceID,
			strPowerCommand,
		]

		self.rpc("instance_server_power_set", arrParams)


	def instance_public_key_get(self, strInstanceI):

		arrParams = [
			strInstanceID,
		]

		return self.rpc("instance_public_key_get", arrParams)


	def instance_server_type_reservation_create(self, strInstanceID, bRecurring, nReservationCycleMonths, nInstallmentCycleMonth):

		arrParams = [
			strInstanceID,
			bRecurring,
			nReservationCycleMonths,
			nInstallmentCycleMonths,
		]

		return Deserializer.deserialize(self.rpc("instance_server_type_reservation_create", arrParams))

	def instance_get(self, strInstanceI):

		arrParams = [
			strInstanceID,
		]

		return Deserializer.deserialize(self.rpc("instance_get", arrParams))

	def instance_array_create(self, strInfrastructureID, objInstanceArra):

		objInstanceArray = Serializer.serialize(objInstanceArray)

		arrParams = [
			strInfrastructureID,
			objInstanceArray,
		]

		return Deserializer.deserialize(self.rpc("instance_array_create", arrParams))

	def instance_array_get(self, strInstanceArrayI):

		arrParams = [
			strInstanceArrayID,
		]

		return Deserializer.deserialize(self.rpc("instance_array_get", arrParams))

	def instance_array_edit(self, strInstanceArrayID, objInstanceArrayOperation, bSwapExistingInstancesHardware = False, bKeepDetachingDrives = None, objServerTypeMatches = None, arrInstanceIDsPreferredForDelete = Non):

		objInstanceArrayOperation = Serializer.serialize(objInstanceArrayOperation)
		objServerTypeMatches = Serializer.serialize(objServerTypeMatches)

		arrParams = [
			strInstanceArrayID,
			objInstanceArrayOperation,
			bSwapExistingInstancesHardware,
			bKeepDetachingDrives,
			objServerTypeMatches,
			arrInstanceIDsPreferredForDelete,
		]

		return Deserializer.deserialize(self.rpc("instance_array_edit", arrParams))

	def instance_array_delete(self, strInstanceArrayI):

		arrParams = [
			strInstanceArrayID,
		]

		return Deserializer.deserialize(self.rpc("instance_array_delete", arrParams))

	def instance_array_start(self, strInstanceArrayI):

		arrParams = [
			strInstanceArrayID,
		]

		return Deserializer.deserialize(self.rpc("instance_array_start", arrParams))

	def instance_arrays(self, strInfrastructureID, arrInstanceArrayIDs = Non):

		arrParams = [
			strInfrastructureID,
			arrInstanceArrayIDs,
		]

		objInstanceArray = self.rpc("instance_arrays", arrParams)
		for strKeyInstanceArray in objInstanceArray:
			objInstanceArray[strKeyInstanceArray] = Deserializer.deserialize(objInstanceArray[strKeyInstanceArray])
		return objInstanceArray

	def instance_array_interface_attach_network(self, strInstanceArrayID, nInstanceArrayInterfaceIndex, strNetworkI):

		arrParams = [
			strInstanceArrayID,
			nInstanceArrayInterfaceIndex,
			strNetworkID,
		]

		return Deserializer.deserialize(self.rpc("instance_array_interface_attach_network", arrParams))

	def instance_array_interface_detach(self, strInstanceArrayID, nInstanceArrayInterfaceInde):

		arrParams = [
			strInstanceArrayID,
			nInstanceArrayInterfaceIndex,
		]

		return Deserializer.deserialize(self.rpc("instance_array_interface_detach", arrParams))

	def instance_array_instances(self, strInstanceArrayID, arrInstanceIDs = Non):

		arrParams = [
			strInstanceArrayID,
			arrInstanceIDs,
		]

		objInstance = self.rpc("instance_array_instances", arrParams)
		for strKeyInstance in objInstance:
			objInstance[strKeyInstance] = Deserializer.deserialize(objInstance[strKeyInstance])
		return objInstance

	def instance_array_stop(self, strInstanceArrayI):

		arrParams = [
			strInstanceArrayID,
		]

		return Deserializer.deserialize(self.rpc("instance_array_stop", arrParams))

	def client_ip(self):

		arrParams = [
		]

		return self.rpc("client_ip", arrParams)


	def subnet_create(self, strNetworkID, objSubne):

		objSubnet = Serializer.serialize(objSubnet)

		arrParams = [
			strNetworkID,
			objSubnet,
		]

		return Deserializer.deserialize(self.rpc("subnet_create", arrParams))

	def subnet_get(self, strSubnetI):

		arrParams = [
			strSubnetID,
		]

		return Deserializer.deserialize(self.rpc("subnet_get", arrParams))

	def subnet_delete(self, strSubnetI):

		arrParams = [
			strSubnetID,
		]

		return Deserializer.deserialize(self.rpc("subnet_delete", arrParams))

	def subnets(self, strNetworkID, arrSubnetIDs = Non):

		arrParams = [
			strNetworkID,
			arrSubnetIDs,
		]

		objSubnet = self.rpc("subnets", arrParams)
		for strKeySubnet in objSubnet:
			objSubnet[strKeySubnet] = Deserializer.deserialize(objSubnet[strKeySubnet])
		return objSubnet

	def network_create(self, strInfrastructureID, objNetwor):

		objNetwork = Serializer.serialize(objNetwork)

		arrParams = [
			strInfrastructureID,
			objNetwork,
		]

		return Deserializer.deserialize(self.rpc("network_create", arrParams))

	def network_get(self, strNetworkI):

		arrParams = [
			strNetworkID,
		]

		return Deserializer.deserialize(self.rpc("network_get", arrParams))

	def network_edit(self, strNetworkID, objNetworkOperatio):

		objNetworkOperation = Serializer.serialize(objNetworkOperation)

		arrParams = [
			strNetworkID,
			objNetworkOperation,
		]

		return Deserializer.deserialize(self.rpc("network_edit", arrParams))

	def network_delete(self, strNetworkI):

		arrParams = [
			strNetworkID,
		]

		return Deserializer.deserialize(self.rpc("network_delete", arrParams))

	def network_start(self, strNetworkI):

		arrParams = [
			strNetworkID,
		]

		return Deserializer.deserialize(self.rpc("network_start", arrParams))

	def network_stop(self, strNetworkI):

		arrParams = [
			strNetworkID,
		]

		return Deserializer.deserialize(self.rpc("network_stop", arrParams))

	def networks(self, strInfrastructureID, arrNetworkIDs = Non):

		arrParams = [
			strInfrastructureID,
			arrNetworkIDs,
		]

		objNetwork = self.rpc("networks", arrParams)
		for strKeyNetwork in objNetwork:
			objNetwork[strKeyNetwork] = Deserializer.deserialize(objNetwork[strKeyNetwork])
		return objNetwork

	def network_join(self, strNetworkID, strNetworkToBeDeletedI):

		arrParams = [
			strNetworkID,
			strNetworkToBeDeletedID,
		]

		return Deserializer.deserialize(self.rpc("network_join", arrParams))

	def resource_utilization_summary(self, strUserIDOwner, strStartTimestamp, strEndTimestamp, arrInfrastructureIDs = Non):

		arrParams = [
			strUserIDOwner,
			strStartTimestamp,
			strEndTimestamp,
			arrInfrastructureIDs,
		]

		return self.rpc("resource_utilization_summary", arrParams)


	def resource_utilization_detailed(self, strUserIDOwner, strStartTimestamp, strEndTimestamp, arrInfrastructureIDs = Non):

		arrParams = [
			strUserIDOwner,
			strStartTimestamp,
			strEndTimestamp,
			arrInfrastructureIDs,
		]

		return self.rpc("resource_utilization_detailed", arrParams)


	def prices(self):

		arrParams = [
		]

		return self.rpc("prices", arrParams)


	def prices_history(self, bExcludeFuturePrices = False, bOnlyActivePrices = Fals):

		arrParams = [
			bExcludeFuturePrices,
			bOnlyActivePrices,
		]

		return self.rpc("prices_history", arrParams)


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

	def server_type_reservation_create(self, strUserID, objReservation, nQuantity = ):

		objReservation = Serializer.serialize(objReservation)

		arrParams = [
			strUserID,
			objReservation,
			nQuantity,
		]

		arrServerTypeReservations = self.rpc("server_type_reservation_create", arrParams)
		for index in range(len(arrServerTypeReservations)):
			arrServerTypeReservations[index] = Deserializer.deserialize(arrServerTypeReservations[index])
		return arrServerTypeReservations

	def server_type_reservation_get(self, nServerTypeReservationI):

		arrParams = [
			nServerTypeReservationID,
		]

		return Deserializer.deserialize(self.rpc("server_type_reservation_get", arrParams))

	def server_type_reservation_edit(self, nServerTypeReservationID, objServerTypeReservatio):

		objServerTypeReservation = Serializer.serialize(objServerTypeReservation)

		arrParams = [
			nServerTypeReservationID,
			objServerTypeReservation,
		]

		return Deserializer.deserialize(self.rpc("server_type_reservation_edit", arrParams))

	def user_server_type_reservations(self, strUserI):

		arrParams = [
			strUserID,
		]

		return self.rpc("user_server_type_reservations", arrParams)


	def user_server_type_reservations_unused(self, strUserID, strDatacenterNam):

		arrParams = [
			strUserID,
			strDatacenterName,
		]

		return self.rpc("user_server_type_reservations_unused", arrParams)


	def shared_drive_create(self, strInfrastructureID, objSharedDriv):

		objSharedDrive = Serializer.serialize(objSharedDrive)

		arrParams = [
			strInfrastructureID,
			objSharedDrive,
		]

		return Deserializer.deserialize(self.rpc("shared_drive_create", arrParams))

	def shared_drive_edit(self, strSharedDriveID, objSharedDriveOperatio):

		objSharedDriveOperation = Serializer.serialize(objSharedDriveOperation)

		arrParams = [
			strSharedDriveID,
			objSharedDriveOperation,
		]

		return Deserializer.deserialize(self.rpc("shared_drive_edit", arrParams))

	def shared_drive_delete(self, strSharedDriveI):

		arrParams = [
			strSharedDriveID,
		]

		return Deserializer.deserialize(self.rpc("shared_drive_delete", arrParams))

	def shared_drive_get(self, strSharedDriveI):

		arrParams = [
			strSharedDriveID,
		]

		return Deserializer.deserialize(self.rpc("shared_drive_get", arrParams))

	def shared_drive_stop(self, strSharedDriveI):

		arrParams = [
			strSharedDriveID,
		]

		return Deserializer.deserialize(self.rpc("shared_drive_stop", arrParams))

	def shared_drive_start(self, strSharedDriveI):

		arrParams = [
			strSharedDriveID,
		]

		return Deserializer.deserialize(self.rpc("shared_drive_start", arrParams))

	def shared_drive_instance_arrays(self, strSharedDriveI):

		arrParams = [
			strSharedDriveID,
		]

		return self.rpc("shared_drive_instance_arrays", arrParams)


	def shared_drive_container_arrays(self, strSharedDriveI):

		arrParams = [
			strSharedDriveID,
		]

		return self.rpc("shared_drive_container_arrays", arrParams)


	def instance_array_shared_drives(self, strInstanceArrayI):

		arrParams = [
			strInstanceArrayID,
		]

		return self.rpc("instance_array_shared_drives", arrParams)


	def shared_drives(self, strInfrastructureID, arrSharedDriveIDs = Non):

		arrParams = [
			strInfrastructureID,
			arrSharedDriveIDs,
		]

		objSharedDrive = self.rpc("shared_drives", arrParams)
		for strKeySharedDrive in objSharedDrive:
			objSharedDrive[strKeySharedDrive] = Deserializer.deserialize(objSharedDrive[strKeySharedDrive])
		return objSharedDrive

	def search(self, strUserID, strKeywords, arrTables = None, objTablesColumns = None, strCollapseType = "array_subrows", arrOrderBy = [], arrLimit = Non):

		objTablesColumns = Serializer.serialize(objTablesColumns)

		arrParams = [
			strUserID,
			strKeywords,
			arrTables,
			objTablesColumns,
			strCollapseType,
			arrOrderBy,
			arrLimit,
		]

		return self.rpc("search", arrParams)


	def query(self, strUserID, strSQLQuery, strCollapseType = "array_subrows):

		arrParams = [
			strUserID,
			strSQLQuery,
			strCollapseType,
		]

		return self.rpc("query", arrParams)


	def query_parse(self, strSQ):

		arrParams = [
			strSQL,
		]

		return self.rpc("query_parse", arrParams)


	def query_structured(self, strUserID, strTableName, objQueryConditions, strCollapseType = "array_subrows):

		objQueryConditions = Serializer.serialize(objQueryConditions)

		arrParams = [
			strUserID,
			strTableName,
			objQueryConditions,
			strCollapseType,
		]

		return self.rpc("query_structured", arrParams)


	def drive_get(self, strDriveI):

		arrParams = [
			strDriveID,
		]

		return Deserializer.deserialize(self.rpc("drive_get", arrParams))

	def drive_edit(self, strDriveID, objDriveOperatio):

		objDriveOperation = Serializer.serialize(objDriveOperation)

		arrParams = [
			strDriveID,
			objDriveOperation,
		]

		return Deserializer.deserialize(self.rpc("drive_edit", arrParams))

	def drive_delete(self, strDriveI):

		arrParams = [
			strDriveID,
		]

		return Deserializer.deserialize(self.rpc("drive_delete", arrParams))

	def drive_attach_instance(self, strDriveID, strInstanceI):

		arrParams = [
			strDriveID,
			strInstanceID,
		]

		return Deserializer.deserialize(self.rpc("drive_attach_instance", arrParams))

	def drive_detach_instance(self, strDriveI):

		arrParams = [
			strDriveID,
		]

		return Deserializer.deserialize(self.rpc("drive_detach_instance", arrParams))

	def instance_drives(self, strInstanceI):

		arrParams = [
			strInstanceID,
		]

		objDrive = self.rpc("instance_drives", arrParams)
		for strKeyDrive in objDrive:
			objDrive[strKeyDrive] = Deserializer.deserialize(objDrive[strKeyDrive])
		return objDrive

	def drive_snapshot_get(self, strSnapshotI):

		arrParams = [
			strSnapshotID,
		]

		return Deserializer.deserialize(self.rpc("drive_snapshot_get", arrParams))

	def drive_snapshot_create(self, strDriveI):

		arrParams = [
			strDriveID,
		]

		return Deserializer.deserialize(self.rpc("drive_snapshot_create", arrParams))

	def drive_snapshot_rollback(self, strSnapshotI):

		arrParams = [
			strSnapshotID,
		]

		self.rpc("drive_snapshot_rollback", arrParams)


	def drive_snapshot_delete(self, strSnapshotI):

		arrParams = [
			strSnapshotID,
		]

		self.rpc("drive_snapshot_delete", arrParams)


	def drive_snapshots(self, strDriveID, arrSnapshotIDs = Non):

		arrParams = [
			strDriveID,
			arrSnapshotIDs,
		]

		objSnapshot = self.rpc("drive_snapshots", arrParams)
		for strKeySnapshot in objSnapshot:
			objSnapshot[strKeySnapshot] = Deserializer.deserialize(objSnapshot[strKeySnapshot])
		return objSnapshot

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

	def drive_array_create(self, strInfrastructureID, objDriveArra):

		objDriveArray = Serializer.serialize(objDriveArray)

		arrParams = [
			strInfrastructureID,
			objDriveArray,
		]

		return Deserializer.deserialize(self.rpc("drive_array_create", arrParams))

	def drive_array_get(self, strDriveArrayI):

		arrParams = [
			strDriveArrayID,
		]

		return Deserializer.deserialize(self.rpc("drive_array_get", arrParams))

	def drive_array_edit(self, strDriveArrayID, objDriveArrayOperation, objDriveArrayEditOptions = {"update_active_drives_size":False):

		objDriveArrayOperation = Serializer.serialize(objDriveArrayOperation)
		objDriveArrayEditOptions = Serializer.serialize(objDriveArrayEditOptions)

		arrParams = [
			strDriveArrayID,
			objDriveArrayOperation,
			objDriveArrayEditOptions,
		]

		return Deserializer.deserialize(self.rpc("drive_array_edit", arrParams))

	def drive_array_delete(self, strDriveArrayI):

		arrParams = [
			strDriveArrayID,
		]

		return Deserializer.deserialize(self.rpc("drive_array_delete", arrParams))

	def drive_array_stop(self, strDriveArrayI):

		arrParams = [
			strDriveArrayID,
		]

		return Deserializer.deserialize(self.rpc("drive_array_stop", arrParams))

	def drive_array_start(self, strDriveArrayI):

		arrParams = [
			strDriveArrayID,
		]

		return Deserializer.deserialize(self.rpc("drive_array_start", arrParams))

	def drive_array_drives(self, strDriveArrayID, arrDriveIDs = Non):

		arrParams = [
			strDriveArrayID,
			arrDriveIDs,
		]

		objDrive = self.rpc("drive_array_drives", arrParams)
		for strKeyDrive in objDrive:
			objDrive[strKeyDrive] = Deserializer.deserialize(objDrive[strKeyDrive])
		return objDrive

	def drive_arrays(self, strInfrastructureID, arrDriveArrayIDs = Non):

		arrParams = [
			strInfrastructureID,
			arrDriveArrayIDs,
		]

		objDriveArray = self.rpc("drive_arrays", arrParams)
		for strKeyDriveArray in objDriveArray:
			objDriveArray[strKeyDriveArray] = Deserializer.deserialize(objDriveArray[strKeyDriveArray])
		return objDriveArray

	def user_create(self, strDisplayName, strLoginEmail, strRedirectURL = None, strAESKey = Non):

		arrParams = [
			strDisplayName,
			strLoginEmail,
			strRedirectURL,
			strAESKey,
		]

		return Deserializer.deserialize(self.rpc("user_create", arrParams))

	def user_get(self, strUserI):

		arrParams = [
			strUserID,
		]

		return Deserializer.deserialize(self.rpc("user_get", arrParams))

	def user_update_language(self, strUserID, strLanguag):

		arrParams = [
			strUserID,
			strLanguage,
		]

		return Deserializer.deserialize(self.rpc("user_update_language", arrParams))

	def user_franchise_get(self, strUserI):

		arrParams = [
			strUserID,
		]

		return self.rpc("user_franchise_get", arrParams)


	def throw_error(self, nErrorCod):

		arrParams = [
			nErrorCode,
		]

		self.rpc("throw_error", arrParams)


	def user_api_key_regenerate(self, strUserI):

		arrParams = [
			strUserID,
		]

		self.rpc("user_api_key_regenerate", arrParams)


	def user_authenticate_password(self, strLoginEmail, strPassword, strOneTimePassword = None, bRememberLogin = True, bTestCredentials = False, bRenewKerberosTicket = Fals):

		arrParams = [
			strLoginEmail,
			strPassword,
			strOneTimePassword,
			bRememberLogin,
			bTestCredentials,
			bRenewKerberosTicket,
		]

		return self.rpc("user_authenticate_password", arrParams)


	def user_authenticate_api_key(self, strUserID, strAPIKey, strOneTimePassword = None, bRememberLogin = Tru):

		arrParams = [
			strUserID,
			strAPIKey,
			strOneTimePassword,
			bRememberLogin,
		]

		return Deserializer.deserialize(self.rpc("user_authenticate_api_key", arrParams))

	def user_authenticate_password_encrypted(self, strLoginEmail, strAESCipherPassword, strRSACipherAESKey, strOneTimePassword = None, bRememberLogin = True, bTestCredentials = False, bRenewKerberosTicket = Fals):

		arrParams = [
			strLoginEmail,
			strAESCipherPassword,
			strRSACipherAESKey,
			strOneTimePassword,
			bRememberLogin,
			bTestCredentials,
			bRenewKerberosTicket,
		]

		return self.rpc("user_authenticate_password_encrypted", arrParams)


	def user_authenticator_has(self, strUserI):

		arrParams = [
			strUserID,
		]

		return self.rpc("user_authenticator_has", arrParams)


	def user_delegate_add(self, strUserID, strDelegateUserEmail, bCreateUserIfNotExists = Fals):

		arrParams = [
			strUserID,
			strDelegateUserEmail,
			bCreateUserIfNotExists,
		]

		self.rpc("user_delegate_add", arrParams)


	def user_delegate_remove(self, strUserID, strDelegateUserEmai):

		arrParams = [
			strUserID,
			strDelegateUserEmail,
		]

		self.rpc("user_delegate_remove", arrParams)


	def user_delegate_children(self, strUserI):

		arrParams = [
			strUserID,
		]

		objUser = self.rpc("user_delegate_children", arrParams)
		for strKeyUser in objUser:
			objUser[strKeyUser] = Deserializer.deserialize(objUser[strKeyUser])
		return objUser

	def user_delegate_parents(self, strUserI):

		arrParams = [
			strUserID,
		]

		objUser = self.rpc("user_delegate_parents", arrParams)
		for strKeyUser in objUser:
			objUser[strKeyUser] = Deserializer.deserialize(objUser[strKeyUser])
		return objUser

	def user_infrastructure_default_set(self, strUserID, strInfrastructureI):

		arrParams = [
			strUserID,
			strInfrastructureID,
		]

		return self.rpc("user_infrastructure_default_set", arrParams)


	def user_infrastructure_default_unset(self, strUserI):

		arrParams = [
			strUserID,
		]

		self.rpc("user_infrastructure_default_unset", arrParams)


	def user_cookie_session(self, bFetchUserLoginSessionData = Fals):

		arrParams = [
			bFetchUserLoginSessionData,
		]

		return Deserializer.deserialize(self.rpc("user_cookie_session", arrParams))

	def user_logout(self):

		arrParams = [
		]

		return self.rpc("user_logout", arrParams)


	def user_limits(self, strUserI):

		arrParams = [
			strUserID,
		]

		return Deserializer.deserialize(self.rpc("user_limits", arrParams))

	def user_change_password(self, strUserID, strNewPassword, strOldPassword = Non):

		arrParams = [
			strUserID,
			strNewPassword,
			strOldPassword,
		]

		self.rpc("user_change_password", arrParams)


	def user_change_password_encrypted(self, strUserID, strAESCipherPassword, strRSACipherAESKey, strOldPassword = Non):

		arrParams = [
			strUserID,
			strAESCipherPassword,
			strRSACipherAESKey,
			strOldPassword,
		]

		self.rpc("user_change_password_encrypted", arrParams)


	def user_prices_history(self, strUserID, bExcludeFuturePrices = False, bOnlyActivePrices = False, bExpandWithPrivateDatacenters = Tru):

		arrParams = [
			strUserID,
			bExcludeFuturePrices,
			bOnlyActivePrices,
			bExpandWithPrivateDatacenters,
		]

		return self.rpc("user_prices_history", arrParams)


	def user_prices(self, strUserI):

		arrParams = [
			strUserID,
		]

		return self.rpc("user_prices", arrParams)


	def user_password_recovery(self, strLoginEmail, strRedirectURL = None, strAESKey = Non):

		arrParams = [
			strLoginEmail,
			strRedirectURL,
			strAESKey,
		]

		self.rpc("user_password_recovery", arrParams)


	def user_create_retry_mail(self, strLoginEmail, strRedirectURL = None, strAESKey = Non):

		arrParams = [
			strLoginEmail,
			strRedirectURL,
			strAESKey,
		]

		self.rpc("user_create_retry_mail", arrParams)


	def user_update_email(self, strUserID, strNewLoginEmail, strRedirectURL = None, strAESKey = Non):

		arrParams = [
			strUserID,
			strNewLoginEmail,
			strRedirectURL,
			strAESKey,
		]

		return self.rpc("user_update_email", arrParams)


	def user_suspend_reasons(self, nUserI):

		arrParams = [
			nUserID,
		]

		arrUserSuspendReasons = self.rpc("user_suspend_reasons", arrParams)
		for index in range(len(arrUserSuspendReasons)):
			arrUserSuspendReasons[index] = Deserializer.deserialize(arrUserSuspendReasons[index])
		return arrUserSuspendReasons

	def user_ssh_key_create(self, strUserID, strSSHKe):

		arrParams = [
			strUserID,
			strSSHKey,
		]

		return Deserializer.deserialize(self.rpc("user_ssh_key_create", arrParams))

	def user_ssh_keys(self, strUserI):

		arrParams = [
			strUserID,
		]

		arrSSHKeys = self.rpc("user_ssh_keys", arrParams)
		for index in range(len(arrSSHKeys)):
			arrSSHKeys[index] = Deserializer.deserialize(arrSSHKeys[index])
		return arrSSHKeys

	def user_ssh_key_delete(self, nSSHKeyI):

		arrParams = [
			nSSHKeyID,
		]

		self.rpc("user_ssh_key_delete", arrParams)


	def data_lake_core_site_conf_download_url(self, strUserID, nDataLakeI):

		arrParams = [
			strUserID,
			nDataLakeID,
		]

		return self.rpc("data_lake_core_site_conf_download_url", arrParams)


	def container_get(self, strContainerI):

		arrParams = [
			strContainerID,
		]

		return Deserializer.deserialize(self.rpc("container_get", arrParams))

	def containers(self, strInfrastructureI):

		arrParams = [
			strInfrastructureID,
		]

		objContainer = self.rpc("containers", arrParams)
		for strKeyContainer in objContainer:
			objContainer[strKeyContainer] = Deserializer.deserialize(objContainer[strKeyContainer])
		return objContainer

	def container_drives(self, strContainerI):

		arrParams = [
			strContainerID,
		]

		objDrive = self.rpc("container_drives", arrParams)
		for strKeyDrive in objDrive:
			objDrive[strKeyDrive] = Deserializer.deserialize(objDrive[strKeyDrive])
		return objDrive

	def container_array_shared_drives(self, strContainerArrayI):

		arrParams = [
			strContainerArrayID,
		]

		return self.rpc("container_array_shared_drives", arrParams)


	def container_logs(self, strContainerID, strSinceTimestamp = None, nLimitBytes = Non):

		arrParams = [
			strContainerID,
			strSinceTimestamp,
			nLimitBytes,
		]

		return self.rpc("container_logs", arrParams)


	def cluster_app(self, strClusterID, bAccessSaaSAPI = True, nAccessSaaSAPITimeoutSeconds = 1):

		arrParams = [
			strClusterID,
			bAccessSaaSAPI,
			nAccessSaaSAPITimeoutSeconds,
		]

		return Deserializer.deserialize(self.rpc("cluster_app", arrParams))

	def container_cluster_app(self, strContainerClusterID, bAccessSaaSAPI = True, nAccessSaaSAPITimeoutSeconds = 1):

		arrParams = [
			strContainerClusterID,
			bAccessSaaSAPI,
			nAccessSaaSAPITimeoutSeconds,
		]

		return Deserializer.deserialize(self.rpc("container_cluster_app", arrParams))

	def container_array_drive_arrays(self, strContainerArrayI):

		arrParams = [
			strContainerArrayID,
		]

		objDriveArray = self.rpc("container_array_drive_arrays", arrParams)
		for strKeyDriveArray in objDriveArray:
			objDriveArray[strKeyDriveArray] = Deserializer.deserialize(objDriveArray[strKeyDriveArray])
		return objDriveArray

	def drive_attach_container(self, strDriveID, strContainerI):

		arrParams = [
			strDriveID,
			strContainerID,
		]

		return Deserializer.deserialize(self.rpc("drive_attach_container", arrParams))

	def drive_detach_container(self, strDriveI):

		arrParams = [
			strDriveID,
		]

		return Deserializer.deserialize(self.rpc("drive_detach_container", arrParams))

	def datacenter_get(self, strUserID, strDatacenterNam):

		arrParams = [
			strUserID,
			strDatacenterName,
		]

		return Deserializer.deserialize(self.rpc("datacenter_get", arrParams))

	def license_types_for_volume_template(self, strVolumeTemplateI):

		arrParams = [
			strVolumeTemplateID,
		]

		return self.rpc("license_types_for_volume_template", arrParams)


	def user_get_brand(self, nUserI):

		arrParams = [
			nUserID,
		]

		return self.rpc("user_get_brand", arrParams)


	def ip_custom_reverse_records(self, strInfrastructureI):

		arrParams = [
			strInfrastructureID,
		]

		return self.rpc("ip_custom_reverse_records", arrParams)


	def ip_custom_reverse_record_remove(self, strInfrastructureID, strIPAddres):

		arrParams = [
			strInfrastructureID,
			strIPAddress,
		]

		self.rpc("ip_custom_reverse_record_remove", arrParams)


	def ip_custom_reverse_record_add(self, strInfrastructureID, strIPAddress, strSubdomainName, strRootDomai):

		arrParams = [
			strInfrastructureID,
			strIPAddress,
			strSubdomainName,
			strRootDomain,
		]

		self.rpc("ip_custom_reverse_record_add", arrParams)


	def container_status(self, strContainerI):

		arrParams = [
			strContainerID,
		]

		return Deserializer.deserialize(self.rpc("container_status", arrParams))

	def container_array_status(self, strContainerArrayI):

		arrParams = [
			strContainerArrayID,
		]

		return Deserializer.deserialize(self.rpc("container_array_status", arrParams))

	def dataset_create(self, strUserID, nTemporaryUploadID, objDatase):

		objDataset = Serializer.serialize(objDataset)

		arrParams = [
			strUserID,
			nTemporaryUploadID,
			objDataset,
		]

		return Deserializer.deserialize(self.rpc("dataset_create", arrParams))

	def dataset_publish(self, nDatasetI):

		arrParams = [
			nDatasetID,
		]

		self.rpc("dataset_publish", arrParams)


	def dataset_unpublish(self, nDatasetI):

		arrParams = [
			nDatasetID,
		]

		self.rpc("dataset_unpublish", arrParams)


	def dataset_edit(self, nDatasetID, nTemporaryUploadID, objChangedDatase):

		objChangedDataset = Serializer.serialize(objChangedDataset)

		arrParams = [
			nDatasetID,
			nTemporaryUploadID,
			objChangedDataset,
		]

		return self.rpc("dataset_edit", arrParams)


	def dataset_datapackage_get(self, nDatasetI):

		arrParams = [
			nDatasetID,
		]

		return Deserializer.deserialize(self.rpc("dataset_datapackage_get", arrParams))

	def dataset_get(self, publishedDatasetI):

		arrParams = [
			publishedDatasetID,
		]

		return Deserializer.deserialize(self.rpc("dataset_get", arrParams))

	def dataset_delete(self, nDatasetI):

		arrParams = [
			nDatasetID,
		]

		self.rpc("dataset_delete", arrParams)


	def datacenter_datasets(self, strDatacenterLabe):

		arrParams = [
			strDatacenterLabel,
		]

		arrDatasets = self.rpc("datacenter_datasets", arrParams)
		for index in range(len(arrDatasets)):
			arrDatasets[index] = Deserializer.deserialize(arrDatasets[index])
		return arrDatasets

	def user_datasets_managed(self, strUserIDOwne):

		arrParams = [
			strUserIDOwner,
		]

		return self.rpc("user_datasets_managed", arrParams)


	def dataset_subscription_create(self, strUserIDOwner, datasetI):

		arrParams = [
			strUserIDOwner,
			datasetID,
		]

		return Deserializer.deserialize(self.rpc("dataset_subscription_create", arrParams))

	def dataset_subscription_delete(self, strUserIDOwner, nDatasetSubscriptionI):

		arrParams = [
			strUserIDOwner,
			nDatasetSubscriptionID,
		]

		self.rpc("dataset_subscription_delete", arrParams)


	def user_dataset_subscriptions(self, strUserIDOwne):

		arrParams = [
			strUserIDOwner,
		]

		arrDatasetSubscriptions = self.rpc("user_dataset_subscriptions", arrParams)
		for index in range(len(arrDatasetSubscriptions)):
			arrDatasetSubscriptions[index] = Deserializer.deserialize(arrDatasetSubscriptions[index])
		return arrDatasetSubscriptions

	def server_instance_oob_allowed_ips(self, strInstanceI):

		arrParams = [
			strInstanceID,
		]

		return self.rpc("server_instance_oob_allowed_ips", arrParams)


	def server_instance_oob_allow_ip(self, strInstanceID, strAllowedI):

		arrParams = [
			strInstanceID,
			strAllowedIP,
		]

		self.rpc("server_instance_oob_allow_ip", arrParams)


	def server_instance_oob_disallow_ip(self, strInstanceID, strDisallowedI):

		arrParams = [
			strInstanceID,
			strDisallowedIP,
		]

		self.rpc("server_instance_oob_disallow_ip", arrParams)


	def instance_array_drive_arrays(self, strInstanceArrayI):

		arrParams = [
			strInstanceArrayID,
		]

		objDriveArray = self.rpc("instance_array_drive_arrays", arrParams)
		for strKeyDriveArray in objDriveArray:
			objDriveArray[strKeyDriveArray] = Deserializer.deserialize(objDriveArray[strKeyDriveArray])
		return objDriveArray

	def infrastructure_lan_subnet_pools_available(self, nInfrastructureI):

		arrParams = [
			nInfrastructureID,
		]

		return self.rpc("infrastructure_lan_subnet_pools_available", arrParams)


	def infrastructure_lan_subnet_prefix_sizes_available(self, nInfrastructureI):

		arrParams = [
			nInfrastructureID,
		]

		return self.rpc("infrastructure_lan_subnet_prefix_sizes_available", arrParams)


	def dataset_readme_upload_url(self):

		arrParams = [
		]

		return self.rpc("dataset_readme_upload_url", arrParams)


	def dataset_readme_download_url(self, nPublicDatasetI):

		arrParams = [
			nPublicDatasetID,
		]

		return self.rpc("dataset_readme_download_url", arrParams)


	def dataset_readme_delete(self, nDatasetI):

		arrParams = [
			nDatasetID,
		]

		self.rpc("dataset_readme_delete", arrParams)


	def drive_array_filesystem_types_available(self):

		arrParams = [
		]

		return self.rpc("drive_array_filesystem_types_available", arrParams)


	def drive_array_block_sizes_available(self):

		arrParams = [
		]

		return self.rpc("drive_array_block_sizes_available", arrParams)


	def cluster_instance_arrays(self, strClusterID, arrInstanceArrayIDs = Non):

		arrParams = [
			strClusterID,
			arrInstanceArrayIDs,
		]

		objInstanceArray = self.rpc("cluster_instance_arrays", arrParams)
		for strKeyInstanceArray in objInstanceArray:
			objInstanceArray[strKeyInstanceArray] = Deserializer.deserialize(objInstanceArray[strKeyInstanceArray])
		return objInstanceArray

	def container_cluster_container_arrays(self, strContainerClusterID, arrContainerArrayIDs = Non):

		arrParams = [
			strContainerClusterID,
			arrContainerArrayIDs,
		]

		objContainerArray = self.rpc("container_cluster_container_arrays", arrParams)
		for strKeyContainerArray in objContainerArray:
			objContainerArray[strKeyContainerArray] = Deserializer.deserialize(objContainerArray[strKeyContainerArray])
		return objContainerArray

	def threshold_create(self, strUserIDOwner, objThreshol):

		objThreshold = Serializer.serialize(objThreshold)

		arrParams = [
			strUserIDOwner,
			objThreshold,
		]

		return Deserializer.deserialize(self.rpc("threshold_create", arrParams))

	def thresholds(self, strUserIDOwne):

		arrParams = [
			strUserIDOwner,
		]

		arrThresholds = self.rpc("thresholds", arrParams)
		for index in range(len(arrThresholds)):
			arrThresholds[index] = Deserializer.deserialize(arrThresholds[index])
		return arrThresholds

	def threshold_edit(self, nThresholdID, objThresholdOperatio):

		objThresholdOperation = Serializer.serialize(objThresholdOperation)

		arrParams = [
			nThresholdID,
			objThresholdOperation,
		]

		return Deserializer.deserialize(self.rpc("threshold_edit", arrParams))

	def threshold_get(self, nThresholdI):

		arrParams = [
			nThresholdID,
		]

		return Deserializer.deserialize(self.rpc("threshold_get", arrParams))

	def threshold_delete(self, nThresholdI):

		arrParams = [
			nThresholdID,
		]

		self.rpc("threshold_delete", arrParams)


	def dataset_subscriptions(self, nDatasetI):

		arrParams = [
			nDatasetID,
		]

		self.rpc("dataset_subscriptions", arrParams)


	def instance_rows(self, strUserID, arrInstanceIDs = Non):

		arrParams = [
			strUserID,
			arrInstanceIDs,
		]

		return self.rpc("instance_rows", arrParams)


	def independent_instance_create(self, strUserIDOwner, strLabel, strDatacenterName, strServerTypeID, arrFirewallRules = [], strISCSIStorageType = "none", nISCSIStorageSizeMBytes = 0, strVolumeTemplateID = Non):

		arrFirewallRules = Serializer.serialize(arrFirewallRules)

		arrParams = [
			strUserIDOwner,
			strLabel,
			strDatacenterName,
			strServerTypeID,
			arrFirewallRules,
			strISCSIStorageType,
			nISCSIStorageSizeMBytes,
			strVolumeTemplateID,
		]

		return Deserializer.deserialize(self.rpc("independent_instance_create", arrParams))

	def independent_instance_delete(self, strInstanceI):

		arrParams = [
			strInstanceID,
		]

		return Deserializer.deserialize(self.rpc("independent_instance_delete", arrParams))

	def independent_instance_storage_expand(self, strInstanceID, nISCSIStorageSizeMByte):

		arrParams = [
			strInstanceID,
			nISCSIStorageSizeMBytes,
		]

		return Deserializer.deserialize(self.rpc("independent_instance_storage_expand", arrParams))

	def instance_label_is_available_assert(self, strUserIDOwner, strInstanceLabe):

		arrParams = [
			strUserIDOwner,
			strInstanceLabel,
		]

		self.rpc("instance_label_is_available_assert", arrParams)


	def jwt_session_cookies_types_to_cookies_names(self):

		arrParams = [
		]

		return self.rpc("jwt_session_cookies_types_to_cookies_names", arrParams)


	def independent_instance_firewall_rules_update(self, strInstanceID, arrFirewallRule):

		arrFirewallRules = Serializer.serialize(arrFirewallRules)

		arrParams = [
			strInstanceID,
			arrFirewallRules,
		]

		return Deserializer.deserialize(self.rpc("independent_instance_firewall_rules_update", arrParams))

	def subnet_prefix_sizes_wan(self, strSubnetTyp):

		arrParams = [
			strSubnetType,
		]

		return self.rpc("subnet_prefix_sizes_wan", arrParams)


	def subnet_prefix_sizes_wan_cluster_attached(self, strSubnetTyp):

		arrParams = [
			strSubnetType,
		]

		return self.rpc("subnet_prefix_sizes_wan_cluster_attached", arrParams)


	def instance_array_interface_create(self, strInstanceArrayI):

		arrParams = [
			strInstanceArrayID,
		]

		return Deserializer.deserialize(self.rpc("instance_array_interface_create", arrParams))

	def infrastructure_ansible_inventory_get(self, strInstanceArrayI):

		arrParams = [
			strInstanceArrayID,
		]

		return self.rpc("infrastructure_ansible_inventory_get", arrParams)


	def infrastructure_ansible_bundles(self, strInfrastructureID, strAnsibleBundleTyp):

		arrParams = [
			strInfrastructureID,
			strAnsibleBundleType,
		]

		return self.rpc("infrastructure_ansible_bundles", arrParams)


	def infrastructure_ansible_bundle_add_into_runlevel(self, strInfrastructureID, nAnsibleBundleID, nRunLeve):

		arrParams = [
			strInfrastructureID,
			nAnsibleBundleID,
			nRunLevel,
		]

		return Deserializer.deserialize(self.rpc("infrastructure_ansible_bundle_add_into_runlevel", arrParams))

	def infrastructure_ansible_bundle_move_into_runlevel(self, strInfrastructureID, nAnsibleBundleID, nSourceRunLevel, nDestinationRunLeve):

		arrParams = [
			strInfrastructureID,
			nAnsibleBundleID,
			nSourceRunLevel,
			nDestinationRunLevel,
		]

		self.rpc("infrastructure_ansible_bundle_move_into_runlevel", arrParams)


	def infrastructure_ansible_bundle_delete_from_runlevel(self, strInfrastructureID, nAnsibleBundleID, nRunLeve):

		arrParams = [
			strInfrastructureID,
			nAnsibleBundleID,
			nRunLevel,
		]

		self.rpc("infrastructure_ansible_bundle_delete_from_runlevel", arrParams)


	def ansible_bundles(self, strUserI):

		arrParams = [
			strUserID,
		]

		objAnsibleBundle = self.rpc("ansible_bundles", arrParams)
		for strKeyAnsibleBundle in objAnsibleBundle:
			objAnsibleBundle[strKeyAnsibleBundle] = Deserializer.deserialize(objAnsibleBundle[strKeyAnsibleBundle])
		return objAnsibleBundle

	def infrastructure_ansible_bundle_exec(self, strInfrastructureID, nInfrastructureAnsibleBundleID, objExtraAnsibleVariables = [):

		objExtraAnsibleVariables = Serializer.serialize(objExtraAnsibleVariables)

		arrParams = [
			strInfrastructureID,
			nInfrastructureAnsibleBundleID,
			objExtraAnsibleVariables,
		]

		return self.rpc("infrastructure_ansible_bundle_exec", arrParams)


	def ansible_bundle_get(self, nAnsibleBundleI):

		arrParams = [
			nAnsibleBundleID,
		]

		return Deserializer.deserialize(self.rpc("ansible_bundle_get", arrParams))

	def ansible_bundle_create(self, strUserID, objAnsibleBundl):

		objAnsibleBundle = Serializer.serialize(objAnsibleBundle)

		arrParams = [
			strUserID,
			objAnsibleBundle,
		]

		return Deserializer.deserialize(self.rpc("ansible_bundle_create", arrParams))

	def ansible_bundle_update(self, nAnsibleBundleID, objAnsibleBundl):

		objAnsibleBundle = Serializer.serialize(objAnsibleBundle)

		arrParams = [
			nAnsibleBundleID,
			objAnsibleBundle,
		]

		return Deserializer.deserialize(self.rpc("ansible_bundle_update", arrParams))

	def ansible_bundle_delete(self, nAnsibleBundleI):

		arrParams = [
			nAnsibleBundleID,
		]

		self.rpc("ansible_bundle_delete", arrParams)


	def secrets(self, strUserID, strUsage = Non):

		arrParams = [
			strUserID,
			strUsage,
		]

		objSecret = self.rpc("secrets", arrParams)
		for strKeySecret in objSecret:
			objSecret[strKeySecret] = Deserializer.deserialize(objSecret[strKeySecret])
		return objSecret

	def secret_get(self, nSecretI):

		arrParams = [
			nSecretID,
		]

		return Deserializer.deserialize(self.rpc("secret_get", arrParams))

	def secret_create(self, strUserID, objSecre):

		objSecret = Serializer.serialize(objSecret)

		arrParams = [
			strUserID,
			objSecret,
		]

		return Deserializer.deserialize(self.rpc("secret_create", arrParams))

	def secret_update(self, nSecretID, objSecre):

		objSecret = Serializer.serialize(objSecret)

		arrParams = [
			nSecretID,
			objSecret,
		]

		return Deserializer.deserialize(self.rpc("secret_update", arrParams))

	def secret_delete(self, nSecretI):

		arrParams = [
			nSecretID,
		]

		self.rpc("secret_delete", arrParams)


	def os_template_create(self, strUserID, objOSTemplat):

		objOSTemplate = Serializer.serialize(objOSTemplate)

		arrParams = [
			strUserID,
			objOSTemplate,
		]

		return Deserializer.deserialize(self.rpc("os_template_create", arrParams))

	def os_templates(self, strUserI):

		arrParams = [
			strUserID,
		]

		objVolumeTemplate = self.rpc("os_templates", arrParams)
		for strKeyVolumeTemplate in objVolumeTemplate:
			objVolumeTemplate[strKeyVolumeTemplate] = Deserializer.deserialize(objVolumeTemplate[strKeyVolumeTemplate])
		return objVolumeTemplate

	def os_template_get(self, nOSTemplateI):

		arrParams = [
			nOSTemplateID,
		]

		return Deserializer.deserialize(self.rpc("os_template_get", arrParams))

	def os_template_update(self, nOSTemplateID, objOSTemplat):

		objOSTemplate = Serializer.serialize(objOSTemplate)

		arrParams = [
			nOSTemplateID,
			objOSTemplate,
		]

		return Deserializer.deserialize(self.rpc("os_template_update", arrParams))

	def os_template_delete(self, nOSTemplateI):

		arrParams = [
			nOSTemplateID,
		]

		self.rpc("os_template_delete", arrParams)


	def infrastructure_tags_add(self, strInfrastructureID, arrInfrastructureTagsName):

		arrParams = [
			strInfrastructureID,
			arrInfrastructureTagsNames,
		]

		return Deserializer.deserialize(self.rpc("infrastructure_tags_add", arrParams))

	def infrastructure_tags_set(self, strInfrastructureID, arrInfrastructureTagsName):

		arrParams = [
			strInfrastructureID,
			arrInfrastructureTagsNames,
		]

		return Deserializer.deserialize(self.rpc("infrastructure_tags_set", arrParams))

	def infrastructure_tags(self, strInfrastructureI):

		arrParams = [
			strInfrastructureID,
		]

		return self.rpc("infrastructure_tags", arrParams)


	def infrastructure_tags_remove(self, strInfrastructureID, arrInfrastructureTagsName):

		arrParams = [
			strInfrastructureID,
			arrInfrastructureTagsNames,
		]

		return Deserializer.deserialize(self.rpc("infrastructure_tags_remove", arrParams))

	def instance_tags_add(self, strInstanceID, arrInstanceTagsName):

		arrParams = [
			strInstanceID,
			arrInstanceTagsNames,
		]

		return Deserializer.deserialize(self.rpc("instance_tags_add", arrParams))

	def instance_tags_set(self, strInstanceID, arrInstanceTagsName):

		arrParams = [
			strInstanceID,
			arrInstanceTagsNames,
		]

		return Deserializer.deserialize(self.rpc("instance_tags_set", arrParams))

	def instance_tags(self, strInstanceI):

		arrParams = [
			strInstanceID,
		]

		return self.rpc("instance_tags", arrParams)


	def instance_tags_remove(self, strInstanceID, arrInstanceTagsName):

		arrParams = [
			strInstanceID,
			arrInstanceTagsNames,
		]

		return Deserializer.deserialize(self.rpc("instance_tags_remove", arrParams))

	def instance_array_tags_add(self, strInstanceArrayID, arrInstanceArrayTagsName):

		arrParams = [
			strInstanceArrayID,
			arrInstanceArrayTagsNames,
		]

		return Deserializer.deserialize(self.rpc("instance_array_tags_add", arrParams))

	def instance_array_tags_set(self, strInstanceArrayID, arrInstanceArrayTagsName):

		arrParams = [
			strInstanceArrayID,
			arrInstanceArrayTagsNames,
		]

		return Deserializer.deserialize(self.rpc("instance_array_tags_set", arrParams))

	def instance_array_tags(self, strInstanceArrayI):

		arrParams = [
			strInstanceArrayID,
		]

		return self.rpc("instance_array_tags", arrParams)


	def instance_array_tags_remove(self, strInstanceArrayID, arrInstanceArrayTag):

		arrParams = [
			strInstanceArrayID,
			arrInstanceArrayTags,
		]

		return Deserializer.deserialize(self.rpc("instance_array_tags_remove", arrParams))

	def os_template_tags_add(self, strVolumeTemplateID, arrOSTemplateTagsName):

		arrParams = [
			strVolumeTemplateID,
			arrOSTemplateTagsNames,
		]

		return Deserializer.deserialize(self.rpc("os_template_tags_add", arrParams))

	def os_template_tags_set(self, strVolumeTemplateID, arrOSTemplateTagsName):

		arrParams = [
			strVolumeTemplateID,
			arrOSTemplateTagsNames,
		]

		return Deserializer.deserialize(self.rpc("os_template_tags_set", arrParams))

	def os_template_tags(self, strVolumeTemplateI):

		arrParams = [
			strVolumeTemplateID,
		]

		return self.rpc("os_template_tags", arrParams)


	def os_template_tags_remove(self, strVolumeTemplateID, arrOSTemplateTagsName):

		arrParams = [
			strVolumeTemplateID,
			arrOSTemplateTagsNames,
		]

		return Deserializer.deserialize(self.rpc("os_template_tags_remove", arrParams))

	def variables(self, strUserID, strUsage = Non):

		arrParams = [
			strUserID,
			strUsage,
		]

		objVariable = self.rpc("variables", arrParams)
		for strKeyVariable in objVariable:
			objVariable[strKeyVariable] = Deserializer.deserialize(objVariable[strKeyVariable])
		return objVariable

	def variable_get(self, nVariableI):

		arrParams = [
			nVariableID,
		]

		return Deserializer.deserialize(self.rpc("variable_get", arrParams))

	def variable_create(self, strUserID, objVariabl):

		objVariable = Serializer.serialize(objVariable)

		arrParams = [
			strUserID,
			objVariable,
		]

		return Deserializer.deserialize(self.rpc("variable_create", arrParams))

	def variable_update(self, nVariableID, objVariabl):

		objVariable = Serializer.serialize(objVariable)

		arrParams = [
			nVariableID,
			objVariable,
		]

		return Deserializer.deserialize(self.rpc("variable_update", arrParams))

	def variable_delete(self, nVariableI):

		arrParams = [
			nVariableID,
		]

		self.rpc("variable_delete", arrParams)


	def os_template_add_os_asset(self, nOSTemplateID, nOSAssetID, strOSAssetFilePat):

		arrParams = [
			nOSTemplateID,
			nOSAssetID,
			strOSAssetFilePath,
		]

		return self.rpc("os_template_add_os_asset", arrParams)


	def os_template_remove_os_asset(self, nOSTemplateID, nOSAssetI):

		arrParams = [
			nOSTemplateID,
			nOSAssetID,
		]

		self.rpc("os_template_remove_os_asset", arrParams)


	def os_template_update_os_asset_path(self, nOSTemplateID, nOSAssetID, strOSAssetFilePat):

		arrParams = [
			nOSTemplateID,
			nOSAssetID,
			strOSAssetFilePath,
		]

		self.rpc("os_template_update_os_asset_path", arrParams)


	def os_template_has_os_asset(self, nOSTemplateID, nOSAssetI):

		arrParams = [
			nOSTemplateID,
			nOSAssetID,
		]

		return self.rpc("os_template_has_os_asset", arrParams)


	def infrastructure_deploy_custom_stages(self, strInfrastructureID, strStageDefinitionTyp):

		arrParams = [
			strInfrastructureID,
			strStageDefinitionType,
		]

		return self.rpc("infrastructure_deploy_custom_stages", arrParams)


	def infrastructure_deploy_custom_stage_add_into_runlevel(self, strInfrastructureID, nStageDefinitionID, nRunLevel, strStageRunGrou):

		arrParams = [
			strInfrastructureID,
			nStageDefinitionID,
			nRunLevel,
			strStageRunGroup,
		]

		return Deserializer.deserialize(self.rpc("infrastructure_deploy_custom_stage_add_into_runlevel", arrParams))

	def infrastructure_deploy_custom_stage_move_into_runlevel(self, strInfrastructureID, nStageDefinitionID, strStageRunGroup, nSourceRunLevel, nDestinationRunLeve):

		arrParams = [
			strInfrastructureID,
			nStageDefinitionID,
			strStageRunGroup,
			nSourceRunLevel,
			nDestinationRunLevel,
		]

		self.rpc("infrastructure_deploy_custom_stage_move_into_runlevel", arrParams)


	def infrastructure_deploy_custom_stage_delete_from_runlevel(self, strInfrastructureID, nStageDefinitionID, nRunLevel, strStageRunGrou):

		arrParams = [
			strInfrastructureID,
			nStageDefinitionID,
			nRunLevel,
			strStageRunGroup,
		]

		self.rpc("infrastructure_deploy_custom_stage_delete_from_runlevel", arrParams)


	def stage_definitions(self, strUserI):

		arrParams = [
			strUserID,
		]

		objStageDefinition = self.rpc("stage_definitions", arrParams)
		for strKeyStageDefinition in objStageDefinition:
			objStageDefinition[strKeyStageDefinition] = Deserializer.deserialize(objStageDefinition[strKeyStageDefinition])
		return objStageDefinition

	def infrastructure_deploy_custom_stage_exec(self, strInfrastructureID, nInfrastructureCustomDeployStageID, objExtraVariables = [):

		objExtraVariables = Serializer.serialize(objExtraVariables)

		arrParams = [
			strInfrastructureID,
			nInfrastructureCustomDeployStageID,
			objExtraVariables,
		]

		return self.rpc("infrastructure_deploy_custom_stage_exec", arrParams)


	def stage_definition_get(self, nStageDefinitionI):

		arrParams = [
			nStageDefinitionID,
		]

		return Deserializer.deserialize(self.rpc("stage_definition_get", arrParams))

	def stage_definition_create(self, strUserID, objStageDefinitio):

		objStageDefinition = Serializer.serialize(objStageDefinition)

		arrParams = [
			strUserID,
			objStageDefinition,
		]

		return Deserializer.deserialize(self.rpc("stage_definition_create", arrParams))

	def stage_definition_update(self, nStageDefinitionID, objStageDefinitio):

		objStageDefinition = Serializer.serialize(objStageDefinition)

		arrParams = [
			nStageDefinitionID,
			objStageDefinition,
		]

		return Deserializer.deserialize(self.rpc("stage_definition_update", arrParams))

	def stage_definition_delete(self, nStageDefinitionI):

		arrParams = [
			nStageDefinitionID,
		]

		self.rpc("stage_definition_delete", arrParams)


	def server_efibootmgr_cleanup(self, nServerI):

		arrParams = [
			nServerID,
		]

		self.rpc("server_efibootmgr_cleanup", arrParams)


	def server_ipmi_users_and_networking_cleanup(self, nServerI):

		arrParams = [
			nServerID,
		]

		self.rpc("server_ipmi_users_and_networking_cleanup", arrParams)


	def server_interfaces_cleanup(self, nServerI):

		arrParams = [
			nServerID,
		]

		self.rpc("server_interfaces_cleanup", arrParams)


	def server_networking_intel_cleanup(self, nServerI):

		arrParams = [
			nServerID,
		]

		self.rpc("server_networking_intel_cleanup", arrParams)


	def server_disks_cleanup(self, nServerI):

		arrParams = [
			nServerID,
		]

		self.rpc("server_disks_cleanup", arrParams)


