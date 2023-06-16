from account.models import User


def run(*args):
    if len(args) != 1:
        print("You need to specify an email address with --script-args <email>. ")
    else:
        try:
            email = str(args[0]).lower()
            user = User.objects.get(email=email)

            print("- Set user role to null")
            user.role = ""

            print("- Set user staff to True")
            user.is_staff = True

            print("- Set user enabled to True")
            user.enabled = True

            user.save()
            print("[V] User successfully modified\n")
        except User.DoesNotExist:
            print("[X] User does not exist.\n")
