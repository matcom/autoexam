class PreguntaController < ApplicationController
  before_action :set_preguntum, only: [:show, :edit, :update, :destroy]

  def index
    @pregunta = Preguntum.all
  end

  def show
  end

  def nueva_pregunta
    @asignatura = Asignatura.find(params[:id])
    @preguntum = Preguntum.new
    @preguntum.asignatura_id = @asignatura.id
    render :new
  end


  def edit
  end

  # POST /pregunta
  # POST /pregunta.json
  def create
    @preguntum = Preguntum.new(preguntum_params)

    respond_to do |format|
      if @preguntum.save
        format.html { redirect_to @preguntum, notice: 'Preguntum was successfully created.' }
        format.json { render action: 'show', status: :created, location: @preguntum }
      else
        format.html { render action: 'new' }
        format.json { render json: @preguntum.errors, status: :unprocessable_entity }
      end
    end
  end

  # PATCH/PUT /pregunta/1
  # PATCH/PUT /pregunta/1.json
  def update
    respond_to do |format|
      if @preguntum.update(preguntum_params)
        format.html { redirect_to @preguntum, notice: 'Preguntum was successfully updated.' }
        format.json { head :no_content }
      else
        format.html { render action: 'edit' }
        format.json { render json: @preguntum.errors, status: :unprocessable_entity }
      end
    end
  end

  # DELETE /pregunta/1
  # DELETE /pregunta/1.json
  def destroy
    @preguntum.destroy
    respond_to do |format|
      format.html { redirect_to pregunta_url }
      format.json { head :no_content }
    end
  end

  private
    # Use callbacks to share common setup or constraints between actions.
    def set_preguntum
      @preguntum = Preguntum.find(params[:id])
    end

    # Never trust parameters from the scary internet, only allow the white list through.
    def preguntum_params
      params.require(:preguntum).permit(:titulo, :asignatura_id, :etiquetas)
    end
end
