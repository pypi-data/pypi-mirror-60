def update_path(boto3:'boto3',path:str)->'boto3':
    """changes the creds path of your boto3 module
    
    Args:
        boto: the boto3 instance to alter
        path: the fully qualified path to the directory where configs and credentials files live

    Returns:
        boto3 module instance with updated defaults
    """
    for updatable in ('credentials_file','config_file',):
        stock=boto3.session.botocore.configprovider.BOTOCORE_DEFAUT_SESSION_VARIABLES[updatable]
        updated=tuple([(attr.replace('~/.aws',path) if isinstance(attr,str) else attr) for attr in stock])
        boto3.session.botocore.configprovider.BOTOCORE_DEFAUT_SESSION_VARIABLES[updatable]=updated
    return boto3
