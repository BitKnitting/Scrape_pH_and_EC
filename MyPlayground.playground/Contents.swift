//: Playground - noun: a place where people can play

import Foundation
if let path = NSBundle.mainBundle().pathForResource("pH_and_EC_values", ofType: "plist") {
    print ("Path to plist: \(path)")
    let fileManager = (NSFileManager .defaultManager())
    if fileManager.fileExistsAtPath(path) {
        if let plants = NSDictionary(contentsOfFile: path) {
            for key in plants.allKeys as! [String] {
                let plant = plants[key]
                print("plant: \(key) pH: \(plant!["pH"]) | EC: \(plant!["EC"])")
            }
        }
    }
}


