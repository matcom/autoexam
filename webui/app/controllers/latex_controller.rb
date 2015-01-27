class LatexController < ApplicationController

  def save_file(examen, filename, content)
    directory = Rails.root.to_s + "/../generated"
    Dir.mkdir(directory) unless File.exists?(directory)
    directory = directory + "/" + examen.directorio
    Dir.mkdir(directory) unless File.exists?(directory)
    filename = directory + "/" + filename
    File.open(filename, "w") do |file|
      file.write(content)
    end
    redirect_to edit_examan_path(examen), :notice => "#{filename} generated successfully"
  end

  def latex_master
    examen = Examan.find(params[:id])
    content = ["% ============================================================================"]
    content << "% #{examen.nombre} "
    content << "% ============================================================================"
    content << "% Lines starting with a % are ignored."
    content << "% Blank lines are ignored as well."
    content << ""
    content << "% the number of questions"
    content << "total: #{examen.cantidad}"
    content << ""
    content << "% the tags that will be used in the test"
    content << "% each tag comes with the minimun number of questions"
    examen.preguntas_por_tema_hash.keys.each do |tag|
      count = examen.preguntas_por_tema_hash[tag]
      string = "@" + tag + ": " + count.to_s
      string += " % warning: this tag has zero question of that type" if count == 0
      content << string
    end
    content << ""
    content << "% here comes the questions"
    content << "--------------------------"
    content << ""

    number = 0
    examen.pregunta.each do |pregunta|
      number += 1
      content << "(#{number}) %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%"
      content << pregunta.listado_de_etiquetas.map {|e| "@" + e}.join(" ") + " % the tags"
      content << pregunta.titulo
      pregunta.opcions.each do |opcion|
        #% Answers with _* are fixed in that position.
        #_* Whoa, no valid answer, is that even possible?
        #% And valid answers can also be fixed with _x*
        #_x* We wouldn't get that far, but is possible.
        string  = "_"
        string += "x" if opcion.right?
        string += " "
        string += opcion.titulo
        content << string
      end
      content << ""
    end

    string   = content.join("\n")
    save_file(examen, "master.txt", string)
  end
end
