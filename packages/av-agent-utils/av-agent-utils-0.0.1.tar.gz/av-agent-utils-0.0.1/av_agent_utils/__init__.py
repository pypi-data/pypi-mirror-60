# gonna just put stuff in here for now, break it up as it grows

import boto3
import gimme_aws_creds.main
import gimme_aws_creds.ui


def okta_login(profile='saas-OktaFirstResponder'):
    roles = '/{}/'.format(profile)
    ui = gimme_aws_creds.ui.CLIUserInterface(argv=['okta_login', '--roles', roles])
    creds = gimme_aws_creds.main.GimmeAWSCreds(ui=ui)

    # Generate credentials overriding profile name with `okta-<account_id>`
    new_profile = None
    for data in creds.iter_selected_aws_credentials():
        arn = data['role']['arn']
        account_id = None
        for piece in arn.split(':'):
            if len(piece) == 12 and piece.isdigit():
                account_id = piece
                break

        if account_id is None:
            raise ValueError("Didn't find aws_account_id (12 digits) in {}".format(arn))

        new_profile = 'okta-{}'.format(account_id)
        data['profile']['name'] = new_profile
        creds.write_aws_creds_from_data(data)

    return boto3.session.Session(profile_name=new_profile)


