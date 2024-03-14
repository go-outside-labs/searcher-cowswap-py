# 🤖🐮 cowsol, a cow arbitrage solver 

<br>


<p align="center">
<img src="https://github.com/go-outside-labs/cowsol-searcher-cowswap-py/assets/138340846/83f76274-2339-4de0-bad9-307ce5b72a63" width="50%" align="center" style="padding:1px;border:1px solid black;"/>
 </p>

<br>

### tl; dr:

##### 🤖 [solvers](https://docs.cow.fi/off-chain-services/solvers) are a key component in the [cow protocol](https://github.com/cowprotocol), serving as the matching engines that find the best execution paths for user orders. in this project, i implement a solver from scratch, running certain arbitrage strategies (*e.g.,* running nelder mead simplex optimization).

##### 📚 more details, check my mirror post, **[on cowsol, an arb solver for CoW protocol](https://mirror.xyz/go-outside.eth/s_RwnRgJvK_6fLYPyav7lFT3Zs4W4ZvYwp-AM9EbuhQ)**.


<br>




---

## current strategies

<br>

### "no market maker" spread arbitrage

> *Spread trades are the act of purchasing one security and selling another related security (legs) as a unit.*

<br>

* **One-leg limit price trade**.
    - In this type of order (*e.g.,* `orders/instance_1.json`), we have a limit price and one pool reserve (*e.g.*, `A -> C`).
* **Two-legged limit price trade for a single execution path**.
    - In this type of order (*e.g.*, `orders/instance_2.json`), we have a two-legged trade (*e.g.*, `A -> B -> C`), with only one option for each leg and it can be solved without any optimization.
* **Two-legs limit price trade for multiple execution paths**.
    - In this type of order (*e.g*., `orders/instance_3.json`), we have a two-legged trade (*e.g.*, `A -> B -> C`) with multiple pool reserves for each leg (*e.g.*, `B1`, `B2`, `B3`), so the order can be completed dividing it through multiple paths and optimizing for maximum total surplus.
<br>


---

## implemented features 

<br>

### liquidity sources

* Support for constant-product AMMs, such as Uniswap v2 (and its forks), where pools are represented by two token balances.


### orders types


* Support for limit price orders for single order instances.
* Support for limit price orders for multiple orders on a single reserve instance.
* Support for limit price orders for multiple orders on multiple reserve instances.


<br>


---


## execution specs

<br>

> *A limit order is an order to buy or sell with a restriction on the maximum price to be paid or the minimum price to be received (the "limit price").*

This limit determines when an order can be executed:

```
limit_price = sell_amount / buy_amount >= executed_buy_amount / executed_sell_amount
```

> *a good rule of thumb is that the [price impact](https://www.paradigm.xyz/2021/04/understanding-automated-market-makers-part-1-price-impact) of your order is about twice the size of your order relative to the pool.*

<br>

### surplus

For multiple execution paths (liquidity sources), we choose the best solution by maximizing the *surplus* of an order:

```
surplus = exec_buy_amount  - exec_sell_amount / limit_price
```

### amounts representation

All amounts are expressed by non-negative integer numbers, represented in atoms (*i.e.*, multiples of $10^{18}$). We add an underline (`_`) to results to denote decimal position, allowing easier reading.

<br>

---

## order specs

<br>

User orders describe a trading intent.

### User order specs

* `sell_token`: token to be sold (added to the amm pool).
* `buy_token`: token to be bought (removed from the amm pool).
* `sell_amount`: limit amount for tokens to be sold.
* `buy_amount`: limit amount for tokens to be bought.
* `exec_sell_amount`: how many tokens get sold after order execution.
* `exec_buy_amount`: how many tokens get bought after order execution.
* `allow_partial_fill`: if `False`, only fill-or-kill orders are executed.
* `is_sell_order`: if it's sell or buy order.

<br>

### AMM exec specs


* `amm_exec_buy_amount`: how many tokens the amm "buys" (gets) from the user, and it's the sum of all `exec_sell_amount` of each path (leg) in the order execution.
* `amm_exec_sell_amount`: how many tokens the amm "sells" (gives) to the user, and it's the sum of all `exec_buy_amount` of each path (leg) in the order execution.
* `market_price`: the price to buy/sell a token through the user order specs.
* `prior_price`: the price to buy/sell a token prior to being altered by the order.
* `prior_sell_token_reserve`: the initial reserve amount of the "sell" token, prior to being altered by the order.
* `prior_buy_token_reserve`: the initial reserve amount of the "buy" token, prior to being altered by the order.
* `updated_sell_token_reserve`: the reserve amount of the "sell" token after being altered by the order.
* `updated_buy_token_reserve`: the reserve amount of the "buy" token after being altered by the order.


<br>


---

## installing

<br>

### Install Requirements


```sh
python3 -m venv venv
source ./venv/bin/activate
make install_deps
```

<br>

### create an `.env`


```sh
cp .env.example .env
vim .env
```

<br>

### Install cowsol

```sh
make install
```

Test your installation:

```
cowsol
```


<br>

---

## usage

<br>

### Listing available pools in an order instance file

```
cowsol -a <order file>
```
<br>

Example output:

```
🐮 AMMs available for orders/instance_1.json

{   'AC': {   'reserves': {   'A': '10000_000000000000000000',
                              'C': '10000_000000000000000000'}}}
```



<br>

### listing orders in an order instance file

```
cowsol -o <order file>
```

<br>

Example output:

```
🐮 Orders for orders/instance_1.json

{   '0': {   'allow_partial_fill': False,
             'buy_amount': '900_000000000000000000',
             'buy_token': 'C',
             'is_sell_order': True,
             'sell_amount': '1000_000000000000000000',
             'sell_token': 'A'}}
```


<br>


### solving a trade for one-leg limit price

```
cowsol -s orders/instance_1.json 
```

<br>

For example, for this user order instance:

<br>

```
{
    "orders": {
        "0": {
            "sell_token": "A",
            "buy_token": "C",
            "sell_amount": "1000_000000000000000000",
            "buy_amount": "900_000000000000000000",
            "allow_partial_fill": false,
            "is_sell_order": true
        }
    },
    "amms": {
        "AC": {
            "reserves": {
                "A": "10000_000000000000000000",
                "C": "10000_000000000000000000"
            }
        }
    }
}

```

<br>

Generates this output (logging set to `DEBUG`):

<br>

```
🐮 Solving orders/instance_1.json.
🐮 Order 0 is a sell order.
🐮 One-leg trade overview:
🐮 ➖ sell 1000_000000000000000000 of A, amm reserve: 10000_000000000000000000
🐮 ➕ buy 900_000000000000000000 of C, amm reserve: 10000_000000000000000000
🟨   Prior sell reserve: 10000_000000000000000000
🟨   Prior buy reserve: 10000_000000000000000000
🟨   Spot sell price 1.0
🟨   Spot buy price 1.0
🟨   AMM exec sell amount: 1000_000000000000000000
🟨   AMM exec buy amount: 909_090909090909090909
🟨   Updated sell reserve: 11000_000000000000000000
🟨   Updated buy reserve: 9090_909090909090909091
🟨   Market sell price 1.21
🟨   Market buy price 0.8264462809917356
🟨   Can fill: True
🐮 TOTAL SURPLUS: 9_090909090909090909
🐮 Results saved at solutions/solution_1_cowsol.json.
```

<br>

And this solution:

<br>

```
{
    "amms": {
        "AC": {
            "sell_token": "C",
            "buy_token": "A",
            "exec_buy_amount": "1000_000000000000000000",
            "exec_sell_amount": "909_090909090909090909"
        }
    },
    "orders": {
        "0": {
            "allow_partial_fill": false,
            "is_sell_order": true,
            "buy_amount": "900_000000000000000000",
            "sell_amount": "1000_000000000000000000",
            "buy_token": "C",
            "sell_token": "A",
            "exec_buy_amount": "909_090909090909090909",
            "exec_sell_amount": "1000_000000000000000000"
        }
    }
}
```

<br>

Note:

* Input orders are located at `orders/`.
* Solutions are located at `solutions/`.


<br>

### two-legged limit price trade for a single execution path

```
cowsol -s orders/instance_2.json 
```

<br>


For example, this user order instance:

<br>

```
{
    "orders": {
        "0": {
            "sell_token": "A",
            "buy_token": "C",
            "sell_amount": "1000_000000000000000000",
            "buy_amount": "900_000000000000000000",
            "allow_partial_fill": false,
            "is_sell_order": true
        }
    },
    "amms": {
        "AB2": {
            "reserves": {
                "A": "10000_000000000000000000",
                "B2": "20000_000000000000000000"
            }
        },        
        "B2C": {
            "reserves": {
                "B2": "15000_000000000000000000",
                "C": "10000_000000000000000000"
            }
        }
    }
}
```

<br>

Generates this (`DEBUG`) output:


```
🐮 Solving orders/instance_2.json.
🐮 Order 0 is a sell order.
🐮 FIRST LEG trade overview:
🐮 ➖ sell 1000_000000000000000000 of A
🐮 ➕ buy some amount of B2
🟨   Prior sell reserve: 10000_000000000000000000
🟨   Prior buy reserve: 20000_000000000000000000
🟨   Spot sell price 0.5
🟨   Spot buy price 2.0
🟨   AMM exec sell amount: 1000_000000000000000000
🟨   AMM exec buy amount: 1818_181818181818181818
🟨   Updated sell reserve: 11000_000000000000000000
🟨   Updated buy reserve: 18181_818181818181818180
🟨   Market sell price 0.605
🟨   Market buy price 1.6528925619834711
🟨   Can fill: True
🐮 SECOND LEG trade overview:
🐮 ➖ sell 1818_181818181818181818 of B2
🐮 ➕ buy some amount of C
🟨   Prior sell reserve: 15000_000000000000000000
🟨   Prior buy reserve: 10000_000000000000000000
🟨   Spot sell price 1.5
🟨   Spot buy price 0.6666666666666666
🟨   AMM exec sell amount: 1818_181818181818181818
🟨   AMM exec buy amount: 1081_081081081081081081
🟨   Updated sell reserve: 16818_181818181818181820
🟨   Updated buy reserve: 8918_918918918918918919
🟨   Market sell price 1.8856749311294765
🟨   Market buy price 0.5303140978816655
🟨   Can fill: True
🐮 TOTAL SURPLUS: 181_081081081081081081
🐮 Results saved at solutions/solution_2_cowsol.json.
```

<br>

And this solution:

<br>


```
{
    "amms": {
        "AB2": {
            "sell_token": "B2",
            "buy_token": "A",
            "exec_buy_amount": "1000_000000000000000000",
            "exec_sell_amount": "1818_181818181818181818"
        },
        "B2C": {
            "sell_token": "C",
            "buy_token": "B2",
            "exec_buy_amount": "1818_181818181818181818",
            "exec_sell_amount": "1081_081081081081081081"
        }
    },
    "orders": {
        "0": {
            "allow_partial_fill": false,
            "is_sell_order": true,
            "buy_amount": "900_000000000000000000",
            "sell_amount": "1000_000000000000000000",
            "buy_token": "C",
            "sell_token": "A",
            "exec_buy_amount": "1081_081081081081081081",
            "exec_sell_amount": "1000_000000000000000000"
        }
    }
}
```

<br>


### two-legged limit price trade for multiple execution paths



<br>

```
cowsol -s orders/instance_3.json 
```

<br>


For example, this user order instance:

<br>

```
{
    "orders": {
        "0": {
            "sell_token": "A",
            "buy_token": "C",
            "sell_amount": "1000_000000000000000000",
            "buy_amount": "900_000000000000000000",
            "allow_partial_fill": false,
            "is_sell_order": true
        }
    },
    "amms": {
        "AB1": {
            "reserves": {
                "A": "10000_000000000000000000",
                "B1": "20000_000000000000000000"
            }
        },
        "AB2": {
            "reserves": {
                "A": "20000_000000000000000000",
                "B2": "10000_000000000000000000"
            }
        },        
        "AB3": {
            "reserves": {
                "A": "12000_000000000000000000",
                "B3": "12000_000000000000000000"
            }
        },        
        "B1C": {
            "reserves": {
                "B1": "23000_000000000000000000",
                "C": "15000_000000000000000000"
            }
        },
        "B2C": {
            "reserves": {
                "B2": "10000_000000000000000000",
                "C": "15000_000000000000000000"
            }
        },
        "B3C": {
            "reserves": {
                "B3": "10000_000000000000000000",
                "C": "15000_000000000000000000"
            }
        }
    }
}

```


<br>

Generates this (`DEBUG`) output:

<br>

```
🐮 Solving orders/instance_3.json.
🐮 Order 0 is a sell order.
🐮 Using the best two execution simulations by surplus yield.
🐮 FIRST LEG trade overview:
🐮 ➖ sell 289_073705673240477696 of A
🐮 ➕ buy some amount of B1
🟨   Prior sell reserve: 10000_000000000000000000
🟨   Prior buy reserve: 20000_000000000000000000
🟨   Spot sell price 0.5
🟨   Spot buy price 2.0
🟨   AMM exec sell amount: 289_073705673240477696
🟨   AMM exec buy amount: 561_904237334502880476
🟨   Updated sell reserve: 10289_073705673240477700
🟨   Updated buy reserve: 19438_095762665497119520
🟨   Market sell price 0.5293251886038823
🟨   Market buy price 1.8891978343927718
🟨   Can fill: True
🐮 SECOND LEG trade overview:
🐮 ➖ sell 561_904237334502880476 of B1
🐮 ➕ buy some amount of C
🟨   Prior sell reserve: 23000_000000000000000000
🟨   Prior buy reserve: 15000_000000000000000000
🟨   Spot sell price 1.5333333333333334
🟨   Spot buy price 0.6521739130434783
🟨   AMM exec sell amount: 561_904237334502880476
🟨   AMM exec buy amount: 357_719965038404924081
🟨   Updated sell reserve: 23561_904237334502880480
🟨   Updated buy reserve: 14642_280034961595075920
🟨   Market sell price 1.609169076200932
🟨   Market buy price 0.6214387380354636
🟨   Can fill: True
🐮 FIRST LEG trade overview:
🐮 ➖ sell 710_926294326759522304 of A
🐮 ➕ buy some amount of B3
🟨   Prior sell reserve: 12000_000000000000000000
🟨   Prior buy reserve: 12000_000000000000000000
🟨   Spot sell price 1.0
🟨   Spot buy price 1.0
🟨   AMM exec sell amount: 710_926294326759522304
🟨   AMM exec buy amount: 671_163952522389243203
🟨   Updated sell reserve: 12710_926294326759522300
🟨   Updated buy reserve: 11328_836047477610756800
🟨   Market sell price 1.1219975504153292
🟨   Market buy price 0.8912675429904732
🟨   Can fill: True
🐮 SECOND LEG trade overview:
🐮 ➖ sell 671_163952522389243203 of B3
🐮 ➕ buy some amount of C
🟨   Prior sell reserve: 10000_000000000000000000
🟨   Prior buy reserve: 15000_000000000000000000
🟨   Spot sell price 0.6666666666666666
🟨   Spot buy price 1.5
🟨   AMM exec sell amount: 671_163952522389243203
🟨   AMM exec buy amount: 943_426540218806186671
🟨   Updated sell reserve: 10671_163952522389243200
🟨   Updated buy reserve: 14056_573459781193813330
🟨   Market sell price 0.7591582673440884
🟨   Market buy price 1.317248382868167
🟨   Can fill: True
🐮 TOTAL SURPLUS: 401_146505257211110752
🐮 Results saved at solutions/solution_3_cowsol.json.
```

<br>

And this solution:

```
{
    "amms": {
        "AB1": {
            "sell_token": "B1",
            "buy_token": "A",
            "exec_sell_amount": "561_904237334502880476",
            "exec_buy_amount": "289_073705673240477696"
        },
        "B1C": {
            "sell_token": "C",
            "buy_token": "B1",
            "exec_sell_amount": "357_719965038404924081",
            "exec_buy_amount": "561_904237334502880476"
        },
        "AB3": {
            "sell_token": "B3",
            "buy_token": "A",
            "exec_sell_amount": "671_163952522389243203",
            "exec_buy_amount": "710_926294326759522304"
        },
        "B3C": {
            "sell_token": "C",
            "buy_token": "B3",
            "exec_sell_amount": "943_426540218806186671",
            "exec_buy_amount": "671_163952522389243203"
        }
    },
    "orders": {
        "0": {
            "allow_partial_fill": false,
            "is_sell_order": true,
            "buy_amount": "900_000000000000000000",
            "sell_amount": "1000_000000000000000000",
            "buy_token": "C",
            "sell_token": "A",
            "exec_buy_amount": "1301_146505257211110752",
            "exec_sell_amount": "1000_000000000000000000"
        }
    }
}
```

<br>

Note: the derivation for the optimization equation for this strategy can be seen [here](docs/).


<br>

----

## features to be added some day

<br>

### strategies


* Add support for more than two legs.
* Add support for more than two pools on two-legged trade.
* Add multiple path graph weighting and cyclic arbitrage detection using the Bellman-Ford algorithm, so that we can optimize by multiple paths without necessarily dividing the order through them. This would allow obtaining arbitrage profit through finding profitable negative cycles (*e.g.*, `A -> B -> C -> D -> A`).


<br>

### liquidity sources

* Add support for Balancer's weighted pools.
* Add support for Uniswap v3 and forks.
* Add support for stable pools.

<br>

### code improvement

* Implement support for AMM fees.
* Add support for concurrency (`async`), so tasks could run in parallel adding temporal advantage to the solver.
* Benchmark and possibly add other optimization algorithms options.
* Add an actual execution class (through CoW server or directly to the blockchains).
* Finish implementing end-to-end BUY limit orders.
* Add unit tests.
* add the bot server (on docker).

<br>


---

## resources

<br>

* [cow.fi](http://cow.fi/)
* [solver specs](https://docs.cow.fi/off-chain-services/in-depth-solver-specification)

  
* [cow protocol support to ERC-1271](https://twitter.com/cowswap/status/1587895229666893824?s=12&t=y-P8Uf4eebJHrHCmZMk7jA&utm_source=substack&utm_medium=email)
* [useful CowSwap resources](https://hackmd.io/@chenm/HJqjdkjvt)
