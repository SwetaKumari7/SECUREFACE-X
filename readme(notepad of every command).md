#### 1\. Every time you want to run the project



Open CMD and run these commands one by one:



cd /d "C:\\Users\\Sweta kumari\\SECURE\_FACE\_AUTHENTICATION\_BACKUP"



Activate virtual environment:



venv\\Scripts\\activate



You should see:



(venv) C:\\Users\\Sweta kumari\\SECURE\_FACE\_AUTHENTICATION\_BACKUP>



Start Flask:



python app.py



You should see:



Database initialized successfully.



SECUREFACE BIOMETRIC AUTHENTICATION

Verification threshold: 0.62

Registered template: models\\face\_templates\_aes.enc



\* Running on http://127.0.0.1:5000



Then open the application:



start http://127.0.0.1:5000/



Dashboard:



start http://127.0.0.1:5000/dashboard



Attack Lab:



start http://127.0.0.1:5000/attack-lab

#### 2\. To stop the project



Go to the CMD running Flask and press:



CTRL + C



That's all.



#### 3\. Before your Attack Lab demonstration



Since you have already generated test events, yes, clean the old security events before a fresh demonstration.



First stop Flask:



CTRL + C



Then:



cd /d "C:\\Users\\Sweta kumari\\SECURE\_FACE\_AUTHENTICATION\_BACKUP"



Run:



python -c "import sqlite3; c=sqlite3.connect('biomatch.db'); c.execute('DELETE FROM security\_events'); c.execute('DELETE FROM authentication\_security'); c.commit(); c.close(); print('Security events cleared. Security counters reset.')"



You should see:



Security events cleared. Security counters reset.

Important



This does NOT delete:



your 200 users

FaceNet

your encrypted template

AES key

blockchain

dataset

model

application



It only clears:



security\_events

authentication\_security

#### 4\. Start fresh after cleaning



Run:



python app.py



Then:



start http://127.0.0.1:5000/dashboard



Your dashboard should show:



REGISTERED SUBJECTS    200

SECURITY EVENTS         0

HIGH SEVERITY           0

BLOCKED ATTEMPTS        0



Threat Monitor:



Current threat level . LOW

Security events ..... 0

High severity ....... 0

Blocked actions ..... 0

System ready



📸 Take your BEFORE ATTACK screenshot here.



#### 5\. Run the Attack Lab



Open:



http://127.0.0.1:5000/attack-lab



Under:



AUTHENTICATION ABUSE



click:



RUN TEST



You should get:



Rejected authentication attempt 1/3

Rejected authentication attempt 2/3

Rejected authentication attempt 3/3

AUTHENTICATION ABUSE DETECTED

DEFENSIVE RESPONSE: SUBJECT LOCKED



Then go back:



http://127.0.0.1:5000/dashboard



You should see:



SECURITY EVENTS       1

HIGH SEVERITY         1

BLOCKED ATTEMPTS      1



and:



Current threat level . ELEVATED



Because your current rule is:



0 high events       → LOW

1–2 high events     → ELEVATED

3+ high events      → CRITICAL



📸 Take your AFTER ATTACK screenshot here.



#### 6\. If you want CRITICAL for the demonstration



Run the Abuse Test three times.



Then:



HIGH SEVERITY = 3



and your dashboard should show:



Current threat level . CRITICAL



However, one test is enough to prove the system works. You don't need to generate unnecessary events.



#### 7\. After finishing the demonstration



If you want your project database clean again, stop Flask:



CTRL + C



and run:



python -c "import sqlite3; c=sqlite3.connect('biomatch.db'); c.execute('DELETE FROM security\_events'); c.execute('DELETE FROM authentication\_security'); c.commit(); c.close(); print('Security events cleared. Security counters reset.')"



Then start normally:



python app.py



Your final dashboard will be:



Security Events       0

High Severity         0

Blocked Attempts      0

Threat Level          LOW



But keep your AFTER ATTACK screenshot for your report/PPT.





