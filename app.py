from flask import Flask , render_template, request, jsonify
from flask_cors import CORS,cross_origin
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen as uReq
import requests
import logging
import os

logging.basicConfig(filename="scrapper.log" , level=logging.INFO)

app = Flask(__name__)  

@app.route("/", methods =['GET'])
def homepage():
    return render_template("index.html")

@app.route("/review", methods=['POST'])
def results():
    if request.method=='POST':
        try:
            searchString = request.form['content'].replace(" ","")
            filename = searchString + ".csv"
            fold_path:str=os.path.join(os.getcwd(),"artifacts")
            try:
                os.makedirs(fold_path,exist_ok=True)
            except Exception as e:
                logging.info(e)

            flipkart_url = "https://www.flipkart.com/search?q=" + searchString
            uClient = uReq(flipkart_url)
            flipkartPage = uClient.read()
            uClient.close()
            flipkart_html= bs(flipkartPage,"html.parser")
            bigboxes= flipkart_html.find_all("div",{"class":"_1AtVbE col-12-12"})
            del bigboxes[0:3]
            box=bigboxes[0]
            productLink= "https://www.flipkart.com" + box.div.div.div.a['href']
            prodRes= uReq(productLink)
            prodpage=prodRes.read()
            prodRes.close()
            prod_html= bs(prodpage,"html.parser")
            comment_boxes= prod_html.find_all("div",{"class":"_16PBlm"})

            #filename = searchString + ".csv"
            #fw=open(filename,"w")          
            headers="Product,Customer Name, Rating, Heading, Comment \n"
            #fw.write(headers)
            with open (os.path.join(fold_path,filename),'w') as f:
                    f.write(headers)
            
                    reviews=[]
                    for commentbox in comment_boxes:
                        try:
                            name = commentbox.div.div.find_all("p",{"class":"_2sc7ZR _2V5EHH"})[0].text
                        except:
                            logging.info("name")
                        try:
                            rating= commentbox.div.div.div.div.text
                        except:
                            rating= "No rating"
                            logging.info("rating")
                        try:
                            commentHead=commentbox.div.div.div.p.text
                        except:
                            commentHead= "No comment Head"
                            logging.info("commentHead")
                        try:
                            comment=commentbox.div.div.find_all("div",{"class":""}).text
                        except:
                            comment="No Comments"
                            logging.info("comment")
                    
                        mydict= {"Product":searchString,"Name":name, "Rating":rating, 
                                "CommentHead":commentHead ,"Comment":comment}
                        reviews.append(mydict)

                        updates=[str(searchString),", ",str(name),", ",str(rating ),", ",str(commentHead ),", ",str(comment)]
                                
                        f.writelines(updates)
                        f.write("\n")
                

            logging.info("final result{}".format(reviews))
            f.close()
            return render_template("results.html",reviews=reviews[0:(len(reviews)-1)])
        
        except Exception as e :
            logging.info(e)
            return "something is wrong"
    
    else :
        return render_template("index.html")


if __name__=="__main__":
    app.run(host="0.0.0.0")


    






