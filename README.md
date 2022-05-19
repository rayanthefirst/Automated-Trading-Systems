# AUTONOMOUS TRADING SYSTEM
In progress and most likely will keep being upgraded with new functionality
## Background
This automated trading system uses trailing stops at its core; many brokerages provide the trailing stop order that can has the ability to limit potential loss without placing a limit on maximum gains.

### Includes:
-Startup manager that controls scheduling, programs as subprocesses
-Bot that executes trades, sends emails, adjusts trail percentages, edits CSV configuration files, records trades to CSV
-Backtester that collects market data, runs strategies and updates bot parameters for next trading session, customizable parameters with manual use

### Future Functionaity:
-Backtesting predicted prices using LSTM machine learning model
-Outside real time hour trading
-Production Code rewritten in C++ for speed up
-Shared memory for Backtestermulti (multiprocessed backtester) to avoid forking on non linux systems
-Trailing amount option
-Stock selector: picks best stocks to use autonomously

<!-- For example:

Lets say we own stock X at $10, we would like to manage our downside risk and so we place a trailing stop sell order at 3%. If the stock falls 3% from the highest point

Additionally, most brokerages let this execution work server side, so you do not have to constantly have a



-risks and best type of things to trade ( high volume) since mkt order
-How the system works - all pieces
-Setup, correct path, ibapi, ibcontroller, config files
![1_9mxrTAU5LQg2Qos4zG6c-Q](https://user-images.githubusercontent.com/99143120/167326914-ce75de56-851e-42a1-92bb-38984915e8cf.png)
 -->
