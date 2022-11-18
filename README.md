# STEM Data Dashboard - TeamMicrosoftPaint
Our Capstone Project repository.

## Important Links
- [Requirements Document](https://docs.google.com/document/d/157iyS07rQm8yJFJeVWR_ZD2b1uBtJpyaRzKcNHmdzCQ/edit)
- [Functional Specification](https://docs.google.com/document/d/1Ypb2SLG7-zbuIucbpgP6dW7aTDYOCHmwdaHG1EaElTI/edit)

## Licensing
- This project is licensed under both the GPL GNU License, and the Mozilla Public License (MPL). Please see the LICENSE file, and see the headers of each file in this repository for more information.

## Important Implementation Notes
- This project is written using Python 3.10.6. Please make sure you have this version or greater installed in order for code to run and interpret correctly.

## Security Implementation
- This project is TLS encryption ready. In order for the server to successfully encrypt data, a private/public key pair must be provided in the `instance` folder. Please generate a key pair using OpenSSL. To do this, issue the following commands: 

        cd instance

        openssl req -x509 -sha256 -nodes -days 365 -newkey rsa:4096 -keyout key.pem -out cert.pem
- This will place two certificates in the `instance` directory, one for the key and another for the certificate.