/* ###########################
#   TYPE CONVERTER FUNCTIONS
############################## */

function b64ToArrayBuffer(base64) {
  let binary_string = window.atob(base64);
  let bytes = new Uint8Array(binary_string.length);

  for (let i = 0; i < binary_string.length; i++) {
    bytes[i] = binary_string.charCodeAt(i);
  }

  return bytes.buffer;
}

function arrayBufferToB64(buffer) {
  let binary = "";
  let bytes = new Uint8Array(buffer);

  for (let i = 0; i < bytes.byteLength; i++) {
    binary += String.fromCharCode(bytes[i]);
  }

  return window.btoa(binary);
}

/* ###########################
#       CRYPTO FUNCTIONS
############################## */

async function PBKDF2SHA256(password, salt, iterations, keyLength) {
  const textEncoder = new TextEncoder("utf-8");
  const passwordBuffer = textEncoder.encode(password);
  const importedKey = await crypto.subtle.importKey(
    "raw",
    passwordBuffer,
    "PBKDF2",
    false,
    ["deriveBits"]
  );
  const saltBuffer = textEncoder.encode(salt);
  const params = {
    name: "PBKDF2",
    hash: "SHA-256",
    salt: saltBuffer,
    iterations: iterations,
  };
  const keyBuffer = await crypto.subtle.deriveBits(
    params,
    importedKey,
    keyLength * 8
  );
  //var derivation = Array.from(new Uint8Array(keyBuffer));

  return keyBuffer;
}

function GenerateRSA() {
  return new Promise((resolve, reject) => {
    let rsa = forge.pki.rsa;
    rsa.generateKeyPair({ bits: 2048, workers: 2 }, function (err, keypair) {
      if (err) {
        reject(err);
        return;
      }
      resolve({
        b64PublicKey: btoa(forge.pki.publicKeyToPem(keypair.publicKey)),
        b64PrivateKey: btoa(forge.pki.privateKeyToPem(keypair.privateKey)),
      });
    });
  });
}

function encryptMessage(key, message) {
  // encrypt some bytes using GCM mode
  let iv = forge.random.getBytesSync(16);

  let cipher = forge.cipher.createCipher("AES-GCM", key);
  cipher.start({
    iv: iv, // should be a 12-byte binary-encoded string or byte buffer
    tagLength: 128, // optional, defaults to 128 bits
  });
  cipher.update(forge.util.createBuffer(message));
  cipher.finish();
  let encrypted = cipher.output;
  let tag = cipher.mode.tag;

  return encrypted.toHex() + "|" + btoa(iv) + "|" + tag.toHex();
}

async function decryptMessage(key, message, iv, tag) {
  var decipher = forge.cipher.createDecipher("AES-GCM", key);
  decipher.start({
    iv: iv,
    tagLength: 128, // optional, defaults to 128 bits
    tag: tag, // authentication tag from encryption
  });
  decipher.update(message);
  var pass = decipher.finish();
  // pass is false if there was a failure (eg: authentication tag didn't match)
  if (pass === false) {
    alert("Authentication tag didn't match");
  }

  return decipher;
}

async function loadCrypto(pubkey, privatekey, symkey) {
  if (sessionStorage.getItem("password") !== null) {
    sessionStorage.setItem("publicKey", pubkey);

    MasterKey = await PBKDF2SHA256(
      atob(sessionStorage.getItem("password")),
      atob(sessionStorage.getItem("mail")),
      600000,
      32
    );
    MasterPasswordHash = await PBKDF2SHA256(
      MasterKey,
      atob(sessionStorage.getItem("password")),
      1,
      64
    );
    var MasterKey_Buffer = forge.util.createBuffer(MasterKey, "raw");

    symkey = symkey.split("|");

    var encrypted = forge.util.createBuffer(forge.util.hexToBytes(symkey[0]));
    var iv = atob(symkey[1]);
    var tag = forge.util.createBuffer(forge.util.hexToBytes(symkey[2]));
    symkey = await decryptMessage(MasterKey_Buffer, encrypted, iv, tag);

    var symkey = forge.util.createBuffer(symkey.output, "raw");

    sessionStorage.setItem("symkey", symkey.toHex());

    privatekey = privatekey.split("|");
    var encrypted = forge.util.createBuffer(forge.util.hexToBytes(privatekey[0]));
    var iv = atob(privatekey[1]);
    var tag = forge.util.createBuffer(forge.util.hexToBytes(privatekey[2]));
    privatekey = await decryptMessage(symkey, encrypted, iv, tag);
    sessionStorage.setItem("privatekey", privatekey.output);

    sessionStorage.removeItem("mail");
    sessionStorage.removeItem("password");
  } else if (sessionStorage.getItem("symkey") === null) {
    return window.location.replace("/logout")
  }


}
