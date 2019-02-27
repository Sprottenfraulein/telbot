from Crypto.Cipher import AES
import modules.db
import base64

cryptor = AES.new('72348t2vdfg45y45y45y3mtv', AES.MODE_CBC, 'g54g4wgw357u77tf')

def authenticate(skeleton_key):
    if len(skeleton_key) == 32:
        pass_hash = base64.b64encode(cryptor.encrypt(skeleton_key)).decode("utf-8")
        print("skeleton key entered:", pass_hash)
        stored_hash = modules.db.get_value('code', 'security', 'name', 'skeletonkey')
        if pass_hash == stored_hash:
            return 1
        else:
            return 0
    else:
        return 0