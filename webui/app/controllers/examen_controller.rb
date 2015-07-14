class ExamenController < ApplicationController
  before_action :set_examan, only: [:show, :edit, :update, :destroy]

  def clave
    @examan = Examan.find(params[:id])
  end

  def show
  end

  def new
    @asignatura = Asignatura.find(params[:id])
    @examan = Examan.new
    @examan.asignatura_id = @asignatura.id
  end

  def edit
    @asignatura = @examan.asignatura
  end

  def get_etiquetas
    list = []
    for etiq in @examan.asignatura.listado_de_etiquetas
      list << etiq if params["etiqueta_#{etiq}"]
    end
    list.join(',')
  end

  def get_preguntas
    list = []
    for etiqueta in @examan.listado_de_etiquetas
      for pregunta in Preguntum.from_etiqueta(etiqueta)
        list << pregunta if params["pregunta_#{pregunta.id}"] && !list.include?(pregunta)
      end
    end
    list
  end

  def get_cantidades
    list = []
    for etiqueta in @examan.listado_de_etiquetas
      list << "#{etiqueta}:#{params["cantidad_#{etiqueta}"]}" if params["cantidad_#{etiqueta}"]
    end
    list.join('|')
  end

  def create
    @examan = Examan.new(examan_params)
    @examan.etiquetas = get_etiquetas

    respond_to do |format|
      if @examan.save
        format.html { redirect_to edit_examan_path(@examan), notice: 'Examan was successfully created.' }
        format.json { render action: 'show', status: :created, location: @examan }
      else
        format.html { render action: 'new' }
        format.json { render json: @examan.errors, status: :unprocessable_entity }
      end
    end
  end

  def update
    @examan.etiquetas = get_etiquetas
    @examan.pregunta = get_preguntas
    @examan.preguntas_por_tema = get_cantidades

    respond_to do |format|
      if @examan.update(examan_params)
        format.html { redirect_to edit_examan_path(@examan), notice: 'Examan was successfully updated.' }
        format.json { head :no_content }
      else
        format.html { render action: 'edit' }
        format.json { render json: @examan.errors, status: :unprocessable_entity }
      end
    end
  end

  # DELETE /examen/1
  # DELETE /examen/1.json
  def destroy
    @examan.destroy
    respond_to do |format|
      format.html { redirect_to examen_url }
      format.json { head :no_content }
    end
  end

  def update_clave
    examan = Examan.find(params[:examan])
    preguntas = examan.pregunta.ordenadas
    content = []
    index = 1
    preguntas.each do |pregunta|
      number = index.to_s
      number += '*' if pregunta.multiple  
      content << number
      index += 1
      content << "total: #{pregunta.opcions.count}"
      clave_pregunta = examan.clave(pregunta)
      minimo = params["minimo_#{pregunta.id}"].to_i
      clave_pregunta.minimo = minimo
      maximo = params["maximo_#{pregunta.id}"].to_i
      clave_pregunta.maximo = maximo
      opciones = ""
      pregunta.opcions.each do |opc|
        clave_opcion = clave_pregunta.clave(opc)
        clave_opcion.puntos_bien = params["opcion_#{clave_opcion.id}_bien"].to_f
        clave_opcion.puntos_mal = params["opcion_#{clave_opcion.id}_mal"].to_f
        opciones = opciones + clave_opcion.puntos_bien.to_s + ':' + 
                   clave_opcion.puntos_mal.to_s + ' '
        clave_opcion.save
      end
      content << opciones
      content << ''
      clave_pregunta.save
    end
    result = save_grader(examan, content)
    redirect_to clave_path(examan, :notice => result)
  end

  def save_grader(examan, content)
    directory = Rails.root.to_s + '/../generated/' + examan.directorio
    return 'Debe crear primero el examen.' if !File.exists?(directory) 
    directory += '/generated/last'
    grader = File.open(directory + '/grader.txt', 'r')
    version = grader.readline
    grader.close
    grader = File.open(directory + '/grader.txt', 'w')
    content.insert(0, version)
    content.insert(1, '')
    content = content.join("\n")
    grader.write(content)
    grader.close
    return 'La clave fue actualizada.'
  end

  private
    # Use callbacks to share common setup or constraints between actions.
    def set_examan
      @examan = Examan.find(params[:id])
    end

    # Never trust parameters from the scary internet, only allow the white list through.
    def examan_params
      params.require(:examan).permit(:nombre, :etiquetas, :directorio, :cantidad, :asignatura_id, :variantes)
    end
end
