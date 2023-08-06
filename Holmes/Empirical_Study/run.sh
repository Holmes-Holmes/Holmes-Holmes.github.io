#!/bin/bash

echo "Please Choose The Consistency of Eco or Name"
read choice

if [ "$choice" == "Eco" ]; then
    python eco_consistency_analysis.py
elif [ "$choice" == "Name" ]; then
    python componentname_inconsistency_analysis.py
elif [ "$choice" == "Acc" ]; then
    cd securitydb_compare 
    python baseline.py
else
    echo "Invalid choice"
fi