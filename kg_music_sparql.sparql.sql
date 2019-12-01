# 查询25个triple
SELECT ?subject ?predicate ?object
WHERE {
	?subject ?predicate ?object
}
LIMIT 25

# -------------------------------------------
# 2. 查询某个歌手演唱的所有歌曲
PREFIX m: <http://kg.course/music/>
SELECT DISTINCT ?trackID
WHERE {
	?trackID m:track_artist m:artist_001
}

# -------------------------------------------
# 3. 想要在上一步的基础上，进一步指导歌曲的名称
PREFIX m: <http://kg.course/music/>
SELECT DISTINCT ?trackID ?name
WHERE {
	?trackID m:track_artist m:artist_001 .
	?trackID m:track_name ?name
}

# -------------------------------------------
# 4. 查询某一首歌曲名称对应的专辑信息
PREFIX m: <http://kg.course/music/>
SELECT DISTINCT ?trackID ?albumID ?album_name
WHERE {
	?trackID m:track_name "track_name_00001" .
	?trackID m:track_album ?albumID . 
	?albumID m:album_name ?album_name
}

# 使用中文定义SPARQL变量
PREFIX m: <http://kg.course/music/>
SELECT DISTINCT ?歌曲id ?专辑id ?专辑名
WHERE {
	?歌曲id m:track_name "track_name_00001" .
	?歌曲id m:track_album ?专辑id . 
	?专辑id m:album_name ?专辑名
}

# 如果还想在查询输出结果的专辑名前面加一些描述文字，应该怎么办呢？
# 可以使用 SPARQL 提供的字符串操作函数 CONCAT 进行字符串连接操作，
# 将描述文字连接到专辑名前面。
PREFIX m: <http://kg.course/music/>
SELECT DISTINCT ?歌曲id ?专辑id (CONCAT("专辑名", ":", ?专辑名) AS ?专辑信息)
WHERE {
	?歌曲id m:track_name "track_name_00001" .
	?歌曲id m:track_album ?专辑id . 
	?专辑id m:album_name ?专辑名
}

# -------------------------------------------
# 5. 查询某个指定专辑内的所有歌曲
PREFIX m: <http://kg.course/music/>
SELECT DISTINCT ?trackID ?track_name
WHERE {
	?albumID m:album_name "album_name_0001" .
	?trackID m:track_album ?albumID . 
	?trackID m:track_name ?track_name .
}

# 如果只需要查找该专辑里面的前 2 首歌曲
PREFIX m: <http://kg.course/music/>
SELECT DISTINCT ?trackID ?track_name
WHERE {
	?albumID m:album_name "album_name_0001" .
	?trackID m:track_album ?albumID . 
	?trackID m:track_name ?track_name .
}
LIMIT 2

-- 如果想知道该专辑中歌曲的确切数目，
-- 可使用聚合函数 COUNT 对歌曲进行计数
PREFIX m: <http://kg.course/music/>
SELECT (COUNT(?trackID) AS ?num) 
WHERE {
	?albumID m:album_name "album_name_0001" .
	?trackID m:track_album ?albumID . 
}

# -------------------------------------------
# 6. 查询某一首歌是哪一个歌手的作品
PREFIX m: <http://kg.course/music/>
SELECT ?trackID ?artistID
WHERE {
	?trackID m:track_name "track_name_00001" .
	?trackID m:track_artist ?artistID .
}


# -------------------------------------------
# 7. 查询某一首歌属于什么歌曲标签
PREFIX m: <http://kg.course/music/>
SELECT ?trackID ?tag_name
WHERE {
	?trackID m:track_name "track_name_00001" .
	?trackID m:track_tag ?tag_name.
}

# -------------------------------------------
# 8. 查询某一歌手唱过歌曲的所有标签
PREFIX m: <http://kg.course/music/>
SELECT ?tag_name
WHERE {
	?trackID m:track_artist m:artist_001 .
	?trackID m:track_tag ?tag_name.
}

# 加上 DISTINCT，即可去掉查询结果中的重复值
PREFIX m: <http://kg.course/music/>
SELECT DISTINCT ?tag_name
WHERE {
	?trackID m:track_artist m:artist_001 .
	?trackID m:track_tag ?tag_name.
}

-- 用户提出要给结果按标签排序。使用 ORDER BY 关键字完成该任务。
-- 只需在上面查询最后加上 ORDER BY ?tag_name 子句，即可将结果按照标签的升序进行排列，如图 3-27 所示。
-- 如果想按照标签降序进行逆向排序，可换为使用 ORDER BY DESC(?tag_name)子句。
PREFIX m: <http://kg.course/music/>
SELECT DISTINCT ?tag_name
WHERE {
	?trackID m:track_artist m:artist_001 .
	?trackID m:track_artist ?tag_name.
}
ORDER BY ?tag_name

# 升序
PREFIX m: <http://kg.course/music/>
SELECT DISTINCT ?tag_name
WHERE {
	?trackID m:track_artist m:artist_001 .
	?trackID m:track_tag ?tag_name.
}
ORDER BY ?tag_name

# 降序
PREFIX m: <http://kg.course/music/>
SELECT DISTINCT ?tag_name
WHERE {
	?trackID m:track_artist m:artist_001 .
	?trackID m:track_tag ?tag_name.
}
ORDER BY DESC(?tag_name)


# -------------------------------------------
# 9. 查询某几类歌曲标签中的歌曲数目

-- 首先，求歌曲数目是一个统计查询，需要用到聚合函数 COUNT。
-- 不妨设求出具有两类标签 tag_name_01 和 tag_name_02 的歌曲数目。
-- 一种方法是分别求出具有每类标签的所有歌曲，然后对这两类歌曲求并集操作；
-- 另一种方法是采用 FILTER 关键字将两类标签设定为歌曲标签的过滤条件。
PREFIX m: <http://kg.course/music/>
SELECT (COUNT(?trackID) AS ?num)
WHERE {
	{ ?trackID m:track_tag "tag_name_01" . }
	UNION
	{ ?trackID M:track_tag "tag_name_02" . }
}

-- 使用FILTER关键字的等价SPARQL查询
PREFIX m: <http://kg.course/music/>
SELECT (COUNT(?trackID) AS ?num)
WHERE {
	?trackID m:track_tag ?tag_name. 
	FILTER (?tag_name = "tag_name_01" || ?tag_name = 'tag_name_02')
}

# -------------------------------------------
# 10. 询问是否存在含有某字符串的歌曲名

-- 分析：该查询不同于之前的所有查询，这是一个 Yes/No 问题。
-- 在 SPARQL 中应该使用 ASK 关键字而不是 SELECT 引导该查询。
-- 而是否含有某字符串的判断可以使用正则表达式匹配函数 regex 完成。
PREFIX m: <http://kg.course/music/>
ASK
WHERE {
	?trackID m:track_name ?track_name .
	FILTER regex(?track_name, "008")
}


# -------------------------------------------
# pART 2. 更新知识图谱
# -------------------------------------------

# -------------------------------------------
# 1. 给歌手 ID 新增属性歌手名字

-- 需要注意的是，在执行 SPARQL 更新语句前，
-- 需要将 Fuseki 用户界面中的 SPARQL Endpoint 由 http://localhost:3030/testds/sparql 
-- 改为 http://localhost:3030/testds/update，
-- 执行该更新操作，如返回的是一段 HTML 文本，
-- 其中含有 Success Update succeeded 字样，则表明更新操作执行成功。

PREFIX m: <http://kg.course/music/>
INSERT DATA {
	m:artist_001 m:artist_name "artist_name_001" .
	m:artist_002 m:artist_name "artist_name_002" .
	m:artist_003 m:artist_name "artist_name_003" .
}


-- 这时，可以执行一个 SPARQL 查询，查看刚刚更新的数据是否产生了作用，该查询的编写和执行留给读者作为练习。（
-- 注意，执行查询前需要再将 SPARQL Endpoint 改回 http://localhost:3030/testds/sparql）
-- e.g. 查询 track_name_00001 的歌手名字
PREFIX m: <http://kg.course/music/>
SELECT ?artist_name
WHERE {
	?trackID m:track_name "track_name_00001" .
	?trackID m:track_artist ?artistID .
	?artistID m:artist_name ?artist_name .
}

# -------------------------------------------
# 2. 删除增加的属性歌手名字

-- 分析：首先使用 WHERE 子句定位要删除的三元组，然后使用 DELETE 子句完成删除操作。
-- 删除歌手 m:artist_002 的名字属性， 构造 SPARQL 更新语句，如图 3-34 所示。
-- 注意，执行删除操作仍然要用 http://localhost:3030/testds/update 作为 SPARQL Endpoint

PREFIX m: <http://kg.course/music/>
DELETE {
	m:artist_002 m:artist_name ?x . 
}
WHERE {
	m:artist_002 m:artist_name ?x .
}


# 查询

PREFIX m: <http://kg.course/music/>
SELECT ?artist_name
WHERE {
	m:artist_002 m:artist_name ?artist_name .
}


PREFIX m: <http://kg.course/music/>
SELECT ?artist_name
WHERE {
	m:artist_001 m:artist_name ?artist_name .
}