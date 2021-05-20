This folder contains example .json schema files which can be passed to reviewer2 using the `--form-schema-json` arg. 
These modify the form that reviewer2 displays on the image page.  

For example, [str_genotypes.json](https://github.com/broadinstitute/reviewer2/blob/main/form_schema_examples/str_genotypes.json)
changes the form from the default:

![image](https://user-images.githubusercontent.com/6240170/118541214-733a4580-b71f-11eb-9348-27c3c94a20ff.png)

to:

![image](https://user-images.githubusercontent.com/6240170/118540459-9adcde00-b71e-11eb-814c-b9063eab1957.png)


The form can be fully customized. For example, [generic.json](https://github.com/broadinstitute/reviewer2/blob/main/form_schema_examples/generic.json)
changes the form to:

![image](https://user-images.githubusercontent.com/6240170/118543032-c3b2a280-b721-11eb-8651-258a378e7bbc.png)

For a list of supported icons (beyond thumbs up, thumbs down), see
https://semantic-ui.com/elements/icon.html

---
To use one of these schemas, you can download the raw json file, edit it if necessary, and pass it to reviewer2 with 
```
python3 -m reviewer2 --form-schema-json path/my_schema.json
```
or if one of the examples is what you want, then you can just pass in the url with 
```
python3 -m reviewer2 --form-schema-json https://github.com/broadinstitute/reviewer2/blob/main/form_schema_examples/str_genotypes.json
```