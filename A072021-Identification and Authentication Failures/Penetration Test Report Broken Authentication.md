# Penetration Test Report Broken Authentication

**Table of Contents**

Sample For Testing

Executive Summary

Attack Narrative

1. ***Sample For Testing***
    - Lab on Port Swigger name “**Broken brute-force protection, multiple credentials per request**”
    - Lab-link: [https://portswigger.net/web-security/authentication/password-based/lab-broken-brute-force-protection-multiple-credentials-per-request](https://portswigger.net/web-security/authentication/password-based/lab-broken-brute-force-protection-multiple-credentials-per-request)
    - Description
        
        ![Untitled](Image_Report/Untitled.png)
        
    - Link Candidate passwords: [https://portswigger.net/web-security/authentication/auth-lab-passwords](https://portswigger.net/web-security/authentication/auth-lab-passwords)
2. ***Attack Narrative***
    - ***Check the username or header***
        - As usual, the first step is to analyze the functionality of the lab at the login feature. I start by finding some general information about the behavior of the brute-force protection, whether it is based on account names, source IPs,…
        - So I try to login with invalid credentials by send it to Burp Repeater and random password.
        
        ![Untitled](Penetration%20Test%20Report%20Broken%20Authentication%2009010b19f26c49e996b9455987823204/Untitled%201.png)
        
        - After three attempts I’m locked out for one minute. The error message in the first three responses is `'Invalid username or password.`, whereas after that it changes to `You have made too many incorrect login attempts. Please try again in 1 minute(s).`
        )
        
        ![Untitled](Penetration%20Test%20Report%20Broken%20Authentication%2009010b19f26c49e996b9455987823204/Untitled%202.png)
        
        ⇒ Therefore, it is not based on usernames but on something that identifies me as the same client, be it IP or another characteristic.
        
        - I try another ways whether the lockout is based on something in the HTTP Headers, this time modifying the User-Agent per request, using the `X-Forwarded-For`
         header and removing or modifying the cookie value. But to no avail, after three attempts the lockout occurs.
            
            ![Untitled](Penetration%20Test%20Report%20Broken%20Authentication%2009010b19f26c49e996b9455987823204/Untitled%203.png)
            

- ***Check the format of request***
    - One thing was here that the request data was not the normal POST data but a JSON structure.
    - We try to change the type data of password:
        
        ![Untitled](Penetration%20Test%20Report%20Broken%20Authentication%2009010b19f26c49e996b9455987823204/Untitled%204.png)
        
    - We don’t the error response, the system may have accepted the array data type of the password without converting it to a string. Thus, it is possible to send all passwords in array format to the system.
    - So from the file password we receive, we change it to the array of password by python.
        
        ![Untitled](Penetration%20Test%20Report%20Broken%20Authentication%2009010b19f26c49e996b9455987823204/Untitled%205.png)
        
        ![Untitled](Penetration%20Test%20Report%20Broken%20Authentication%2009010b19f26c49e996b9455987823204/Untitled%206.png)
        
        ![Untitled](Penetration%20Test%20Report%20Broken%20Authentication%2009010b19f26c49e996b9455987823204/Untitled%207.png)
        
    - Send request with array password we have:
        
        ![Untitled](Penetration%20Test%20Report%20Broken%20Authentication%2009010b19f26c49e996b9455987823204/Untitled%208.png)
        
    - We have status code 302, so we copy and paste URL in browser by Show response in browser. However, we have not found the password of `carlos`, we just logged in as `carlos`
        
        ![Untitled](Penetration%20Test%20Report%20Broken%20Authentication%2009010b19f26c49e996b9455987823204/Untitled%209.png)
