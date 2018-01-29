<!DOCTYPE html>
<html lang="en">
   <head>
      <link href="http://getbootstrap.com/dist/css/bootstrap.min.css" rel="stylesheet">
      <link href="http://getbootstrap.com/examples/jumbotron-narrow/jumbotron-narrow.css" rel="stylesheet">
   </head>
   <body>
          
      <div class="container">
                 
         <div class="jumbotron">
                        
            <h1>FILE UPLOADED: {{user_file.filename}}</h1>

            <div><p><?php include('test.txt'); ?></p></div>
            
            <p class="lead"></p>

            <form action = "http://localhost:5000/uploader" method = "POST" 
               enctype = "multipart/form-data">
               <input type = "file" name = "file" />
               <input type = "submit"/>
            </form>
            <br>

            <p><a class="btn btn-lg btn-success" href="showSignUp" role="button">Run</a></p>
            <p><a class="btn btn-lg btn-success" href="showSignUp" role="button">Update</a></p>
            <p><a class="btn btn-lg btn-success" href="showSignUp" role="button">Runupdate</a></p>
            <p><a class="btn btn-lg btn-success" href="showSignUp" role="button">Merge</a></p>
            
         </div>
          
                 
         <div class="row marketing">
                        
            <div class="col-lg-6">
                               
               <h4>Run</h4>
                               
               <p>Donec id elit non mi porta gravida at eget metus. Maecenas faucibus mollis interdum.</p>
                
                               
               <h4>Update</h4>
                               
               <p>Morbi leo risus, porta ac consectetur ac, vestibulum at eros. Cras mattis consectetur purus sit amet fermentum.</p>
                           
            </div>
             
                        
            <div class="col-lg-6">
                               
               <h4>Runupdate</h4>
                               
               <p>Donec id elit non mi porta gravida at eget metus. Maecenas faucibus mollis interdum.</p>
                
                               
               <h4>Merge</h4>
                               
               <p>Morbi leo risus, porta ac consectetur ac, vestibulum at eros. Cras mattis consectetur purus sit amet fermentum.</p>
                           
            </div>
                    
         </div>
          
                 
         <footer class="footer">
                    
            <p>&copy; Company 2015</p>
                
         </footer>
          
             
      </div>
   </body>
    
</html>