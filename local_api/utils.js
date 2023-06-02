import { MongoClient } from "mongodb"
import {service_account}from "./service_account.js"

const client = new MongoClient(service_account.KEY)
const db =  client.db("cam_manager")

export function checkLicense(req,res){
    const {mid, feed_url}=req.body
        console.log("Recieved: ", req.body)

        db.collection("licenses").find({mid}).toArray()
        .then(licenses=>{
            const license=licenses[0]

            if(license.mid==mid && license.feed_urls.includes(feed_url) ){
                res.status(200).send({license:"valid",response:"OK!"})
            }else{
                res.status(200).send({license:"invalid",response:"OK!"})
            }
        
            console.log("API verify route pinged...")
        })
 
}


export function postMultipleFeeds(req,res){
    const {buffer}=req.body
  
    // console.log("Recieved: ", updateMany)

    // const toUpdateWithTimeStamp = updateMany.map((el)=>{
    //     el.createdAt = { $currentDate: { type: 'date' } }
    //     return el
    // })
    // console.log(toUpdateWithTimeStamp)
    
   if (buffer.length > 0) db.collection("feeds").insertMany(buffer)
    .then((result,error)=>{

        if(error) res.status(400).send({response:"Server error!"})
        else res.status(200).send({response:"OK!"})

        console.log("result: ", result)
        console.log("error: ", error)
    })
}

export function postSingleFeed(req,res){
    const {machine_event, machine}=req.body

    console.log("Recieved: ", req.body)

    // const toUpdateWithTimeStamp = toUpdate.map((el)=>{
    //     el.createdAt = { $currentDate: { type: 'date' } }
    //     return el
    // })
    // console.log(toUpdateWithTimeStamp)
    const feedSingle={
        machine_event,
        machine
    }
    
    db.collection("feeds").insertOne(feedSingle)
    .then((result,error)=>{

        if(error) res.status(400).send({response:"Server error!"})
        else res.status(200).send({response:"OK!"})

        console.log("result: ", result)
        console.log("error: ", error)
    })
}