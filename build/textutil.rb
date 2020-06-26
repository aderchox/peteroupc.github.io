def prepareMarkdown(data)
  contents=""
  headings=[]
  slugs=[]
  data=data.gsub(/<a\s+(id|name)[^>]*>\s*<\/a>/,"")
  data=data.gsub(/\t/," "*8)
  notetexts={}
  textstorefs={} # to help remove duplicate note texts
  data.scan(/<sup\s+id\s*\=\s*([^>]+)>\s*\(\d+\)\s*<\/sup>\s*([\s\S]+?)(?=<sup\s+id|\#\#|\z)/){|n|
    notetext=n[1].gsub(/\s+\z/,"")
    notetext=notetext.gsub(/<\/?small>/,"").gsub(/\s+\z/,"")
    textstorefs[notetext]=n[0] if !textstorefs[notetext]
    notetexts[n[0]]=notetext
  }
  noterefs={} # Associates old note refs with new refs
  newnotetexts=[]
  data=data.gsub(/<sup>\s*\[(?:\*\*)?\(\d+\)(?:\*\*)?\]\s*\(\#([^>]+)\)\s*<\/sup>/){
     noteref=$1
     newrefid=""
     newref=0
     ntext=notetexts[noteref] || "No note text yet."
     # Use canonical note reference for note text,
     # to avoid duplicate note texts
     noteref=textstorefs[ntext] || noteref
     if !noterefs[noteref]
       newref=newnotetexts.length
       newrefid="Note#{newref+1}"
       noterefs[noteref]=newref
       ntext=notetexts[noteref] || "No note text yet."
       ntext="<sup id=#{newrefid}>(#{newref+1})</sup> "+ntext
       newnotetexts.push("<small>"+ntext+"</small>")
     else
       newref=noterefs[noteref]
       newrefid="Note#{newref+1}"
     end
     next "<sup>[(#{newref+1})](##{newrefid})</sup>"
  }
  data=data.gsub(/<<([^\|>\n]*)\|([^\|>]+)>>/){
     noteref=$1||""
     notedata=$2
     next $& if noteref[/^\s+/] # sanity check
     newref=newnotetexts.length
     newrefid="Note#{newref+1}"
     noterefs[noteref]=newref
     ntext=notedata
     ntext="<sup id=#{newrefid}>(#{newref+1})</sup> "+ntext
     newnotetexts.push("<small>"+ntext+"</small>")
     noterefparen=(noteref.length==0) ? "" : "(#{noteref})"
     next noterefparen+"<sup>[(#{newref+1})](##{newrefid})</sup>"
  }

  data=data.gsub(/<sup\s+id[\s\S]+?(?=\#\#|\z)/){
    next newnotetexts.join("\n\n")+"\n\n"
  }
  data.scan(/^(\#\#+)\s+(.*)\s+?/){|heading|
   h0=heading[0]
   h1=heading[1]
   h1=h1.gsub(/<a\s+(id|name)[^>]*>\s*<\/a>/,"").gsub(/\s+$/,"")
   headings.push(h1)
   indent=" "*(4*(h0.length-2))+"- "
   h1slug=h1.gsub(/<[^>]*>/,"").gsub(/\W+/,"_").gsub(/^_+|_+$/,"")
   origslug=h1slug
   sindex=2
   while slugs.include?(h1slug)
     h1slug=origslug+"_#{sindex}"
     sindex+=1
   end
   slugs.push(h1slug)
   h1c=h1.gsub(/([\[\]])/) { "\\#{$1}" }
   contents+=indent+"["+h1c+"](##{h1slug})\n"
  }
  data=data.gsub(/^(\#\#+)\s+(Contents\b.*)\n+([\s\S]+?)(?=\#\#|\z)/){
   ret="#{$1} #{$2}\n\n"+contents+"\n\n"
   next ret
  }
  data=data.gsub(/^(\#\#+)[ \t]+(Notes\b.*)\n+([\s\S]*?)(?=\#\#|\z)/){
   p1=$1
   p2=$2
   nt=$3
   nt=nt.gsub(/\A\s+|\s+\z/,"")
   nt=nt.gsub(/(<small>\s*)+/,"<small>")
   ret="#{p1} #{p2}\n\n"+nt+"\n\n"
   next ret
  }
  data=data.gsub(/(\A|[^\\])\[(?!\*\*)([^\]\n]+)\]\(/){
   ret="#{$1}[**#{$2}**]("
   next ret
  }
  data=data.gsub(/\*\*\*\*+\]\(/,"**](")
  index=0
  data=data.gsub(/^(\#\#+)\s+(.*)\r?/){
   ret="<a id=#{slugs[index]}></a>\n#{$1} #{headings[index]}"
   index+=1
   next ret
  }
  if data.include?("<<Index:") && data.include?("## Index")
    headingre= /(<a\s+(?:id|name)\s*=\s*([^>]+)>\s*<\/a>\s*\#\#+\s+(.*)\s+?)/
    headingres= /(?:<a\s+(?:id|name)\s*=\s*(?:[^>]+)>\s*<\/a>\s*\#\#+\s+(?:.*)\s+?)/
    sections=data.split(headingres)
    iheadings=[];data.scan(headingre){|m|
      iheadings.push(m)
    }
    links=[]
    for i in 1...sections.length
      iheading=iheadings[i-1]
      sections[i]=sections[i].gsub(/<<\s*Index\:\s*([^>]+)>>/){
        items=$1
        items=items.split(/\s*\|\s*/)
        for item in items
          links.push("- **#{item}**: See [**#{iheading[2]}**](##{iheading[1]}).")
        end
        next ""
      }
    end
    links.sort!
    for i in 1...sections.length
      iheading=iheadings[i-1]
      if iheading[2]=="Index"
         sections[i]=links.join("\n")+"\n"+sections[i]
      end
    end
    newdata=[sections[0]]
    for i in 1...sections.length
      iheading=iheadings[i-1]
      newdata.push(iheading[0])
      newdata.push(sections[i])
    end
    data=newdata.join("")
  end
  return data
end
