#coding: utf-8
from collections import defaultdict

import MySQLdb
from flask import Flask, render_template, redirect, url_for, request, jsonify

app = Flask(__name__)

DB_PARAM = {"user":   'root',
            "passwd": '',
            "host":   'localhost',
            "db":     'analyze_tree'}

def build_tree(partial_tree, val):
    return {id_: {'children': build_tree(partial_tree, id_)} for id_ in partial_tree[val]}

@app.route("/")
def index():
    nodes = select_node()
    return render_template('index.html', nodes=nodes)

@app.route("/get")
def get():
    results = select_reference()

    # ツリーの部品を作る
    partial_tree = defaultdict(list)
    for row in results:
        partial_tree[row[1]].append(row[0])
    print(partial_tree)

    # ツリーを組み上げる
    tree = build_tree(partial_tree, 1)

    return jsonify({'tree': tree})

@app.route("/delete", methods=["POST"])
def delete():
    node_id = request.form["id"]
    assert node_id != 1, "ルートのノードは消せない"

    with MySQLdb.connect(**DB_PARAM) as cur:
        # 指定したノードと子のノードを消す
        sql = "DELETE FROM reference WHERE id={} OR parent_id={};".format(node_id, node_id)
        cur.execute(sql)

    return redirect(url_for("index"))

@app.route("/add", methods=["POST"])
def add():
    node_id = request.form["id"]
    label = request.form["label"]

    # Todo: トランザクションを入れる
    with MySQLdb.connect(**DB_PARAM) as cur:
        # 新しいノードを INSERT
        sql = "INSERT INTO node(label) VALUES('{}');".format(label)
        cur.execute(sql)

        # 新しく作られたノードの id を取得する
        sql = "SELECT LAST_INSERT_ID();"
        cur.execute(sql)
        new_node_id = cur.fetchall()[0][0]

        # 追加対象のノードの親の node_id を全取得
        sql = "SELECT parent_id FROM reference WHERE id={};".format(node_id)
        cur.execute(sql)

        rows = cur.fetchall()
        parent_ids = []
        for row in rows:
            parent_ids.append(row[0])

        assert parent_ids != [], "該当する親ノードがありません"

        # 親との関係を登録
        sql = "INSERT INTO reference(id, parent_id, `is_direct`) VALUES({}, {}, {});".format(new_node_id, node_id, 1)
        cur.execute(sql)

        # 祖父との関係を登録
        for parent_id in parent_ids:
            # Todo: クエリ 1 回でレコードを全て INSERT する
            sql = "INSERT INTO reference(id, parent_id, `is_direct`) VALUES({}, {}, {});".format(new_node_id, parent_id, 0)
            cur.execute(sql)

    return redirect(url_for("index"))

@app.route("/move", methods=["POST"])
def move():
    from_id = request.form["from_id"]
    to_id = request.form["to_id"]

    # Todo: トランザクションを入れる
    with MySQLdb.connect(**DB_PARAM) as cur:
        # 移動する子の node_id の一覧を取得
        sql = "SELECT id FROM reference WHERE parent_id={};".format(from_id)
        cur.execute(sql)

        rows = cur.fetchall()
        child_ids = []
        for row in rows:
            child_ids.append(row[0])

        # 移動するノードの関係を削除
        sql = "DELETE FROM reference WHERE id={} OR parent_id={};".format(from_id, from_id)
        cur.execute(sql)

        ### 親のノードの移動
        # 追加対象のノードの親の node_id を全取得
        sql = "SELECT parent_id FROM reference WHERE id={};".format(to_id)
        cur.execute(sql)

        rows = cur.fetchall()
        parent_ids = []
        for row in rows:
            parent_ids.append(row[0])

        # 親との関係を登録
        sql = "INSERT INTO reference(id, parent_id, `is_direct`) VALUES({}, {}, {});".format(from_id, to_id, 1)
        cur.execute(sql)

        # 祖父との関係を登録
        for parent_id in parent_ids:
            # Todo: クエリ 1 回でレコードを全て INSERT する
            sql = "INSERT INTO reference(id, parent_id, `is_direct`) VALUES({}, {}, {});".format(from_id, parent_id, 0)
            cur.execute(sql)

        ### 子のノードの移動
        for child_id in child_ids:
            # 移動先の親との関係性登録
            sql = "INSERT INTO reference(id, parent_id, `is_direct`) VALUES({}, {}, {});".format(child_id, to_id, 1)
            cur.execute(sql)

            # 移動先の祖父との関係性登録
            for parent_id in parent_ids:
                sql = "INSERT INTO reference(id, parent_id, `is_direct`) VALUES({}, {}, {});".format(child_id, parent_id, 0)
                cur.execute(sql)

    return redirect(url_for("index"))

def select_node():
    with MySQLdb.connect(**DB_PARAM) as cur:
        sql = "SELECT * FROM node;"
        cur.execute(sql)
        rows = cur.fetchall()

    return rows

def select_reference():
    with MySQLdb.connect(**DB_PARAM) as cur:
        sql = "SELECT id, parent_id FROM reference WHERE is_direct = 1;"
        cur.execute(sql)
        rows = cur.fetchall()

    return rows

if __name__ == "__main__":
    app.run(use_reloader=False)
