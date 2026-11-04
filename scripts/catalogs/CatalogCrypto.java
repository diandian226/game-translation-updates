import java.nio.file.*;
import java.security.*;
import java.security.cert.*;
import java.security.spec.PKCS8EncodedKeySpec;
import java.util.Base64;

/** Public signing utility. Private key bytes are read locally, never printed or bundled. */
public final class CatalogCrypto {
    public static void main(String[] args) throws Exception {
        if (args.length != 4) throw new IllegalArgumentException("verify|sign certificate payload signature-or-private-key");
        java.security.cert.Certificate cert;
        try (java.io.InputStream in = Files.newInputStream(Paths.get(args[1]))) {
            cert = CertificateFactory.getInstance("X.509").generateCertificate(in);
        }
        byte[] payload = Files.readAllBytes(Paths.get(args[2]));
        if (payload.length == 0 || payload.length > 512 * 1024) throw new SecurityException("Envelope payload size invalid");
        Signature signature = Signature.getInstance("SHA256withRSA");
        if (args[0].equals("verify")) {
            signature.initVerify(cert);
            signature.update(payload);
            if (!signature.verify(Files.readAllBytes(Paths.get(args[3])))) throw new SecurityException("Signature invalid");
            System.out.println("VERIFIED");
        } else if (args[0].equals("sign")) {
            PrivateKey key = KeyFactory.getInstance("RSA").generatePrivate(new PKCS8EncodedKeySpec(Files.readAllBytes(Paths.get(args[3]))));
            signature.initSign(key);
            signature.update(payload);
            byte[] signed = signature.sign();
            signature.initVerify(cert);
            signature.update(payload);
            if (!signature.verify(signed)) throw new SecurityException("Private key does not match trusted certificate");
            System.out.println(Base64.getEncoder().encodeToString(signed));
        } else throw new IllegalArgumentException("Unknown operation");
    }
}
