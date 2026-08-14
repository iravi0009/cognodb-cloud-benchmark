import socket
import ssl

HOST = "db-7530b7a5.databases.cognodb.com"
PORT = 7687


def test_tls(version_name, tls_version):
    print(f"\nTesting {version_name}...")

    context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE
    context.minimum_version = tls_version
    context.maximum_version = tls_version

    try:
        with socket.create_connection((HOST, PORT), timeout=10) as sock:
            with context.wrap_socket(sock, server_hostname=HOST) as tls_sock:
                print("SUCCESS")
                print("TLS version:", tls_sock.version())
                print("Cipher:", tls_sock.cipher())

    except Exception as e:
        print("FAILED")
        print(type(e).__name__, ":", e)


test_tls("TLS 1.2", ssl.TLSVersion.TLSv1_2)
test_tls("TLS 1.3", ssl.TLSVersion.TLSv1_3)